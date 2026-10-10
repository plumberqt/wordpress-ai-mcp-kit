<?php
/**
 * Plugin Name:       AI Office Hours
 * Plugin URI:        https://github.com/plumberqt/wordpress-ai-mcp-kit
 * Description:       Time-boxed access for the AI agent user. Day role during office hours, read-only lock otherwise. Weekly off, holidays, manual Grant/Revoke, capability checkboxes.
 * Version:           1.0.0
 * Author:            plumberqt
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       ai-office-hours
 * Requires at least: 6.0
 * Requires PHP:      7.4
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'AOH_VERSION', '1.0.0' );
define( 'AOH_CRON_HOOK', 'aoh_hourly_tick' );

/* ---------------------------------------------------------------- helpers */

function aoh_default_settings() {
	return array(
		'auto_enabled' => 1,
		'start'        => '10:30',
		'end'          => '18:30',
		'off_day'      => '3', // 0=Sun .. 6=Sat, 3=Wednesday, -1=no weekly off
		'holidays'     => array(), // list of Y-m-d
		'target_user'  => 0,
		'day_role'     => 'ai_day',
		'night_role'   => 'ai_night',
		'extras'       => array( 'edit_theme_options' => 1 ),
	);
}

function aoh_get_settings() {
	$saved = get_option( 'aoh_settings', array() );
	if ( ! is_array( $saved ) ) {
		$saved = array();
	}
	$s = wp_parse_args( $saved, aoh_default_settings() );
	$s['holidays'] = array_values( array_filter( (array) $s['holidays'] ) );
	$s['extras']   = is_array( $s['extras'] ) ? $s['extras'] : array();
	return $s;
}

function aoh_now() {
	return new DateTimeImmutable( 'now', wp_timezone() );
}

function aoh_extras() {
	return array(
		'edit_theme_options' => 'Styling &amp; Menus (Customizer, FSE templates, menus)',
		'unfiltered_html'    => 'Raw HTML/JS in content (unfiltered_html)',
		'activate_plugins'   => 'Activate / deactivate plugins',
		'install_plugins'    => 'Install or update plugins',
		'switch_themes'      => 'Switch theme',
		'manage_options'     => 'Site settings / options (DANGEROUS)',
		'create_users'       => 'Create new users',
		'promote_users'      => 'Change user roles',
		'delete_users'       => 'Delete users (DANGEROUS)',
	);
}

function aoh_is_open( $s, $now = null ) {
	$now = $now ? $now : aoh_now();

	$off_day = isset( $s['off_day'] ) ? (int) $s['off_day'] : -1;
	if ( $off_day >= 0 && (int) $now->format( 'w' ) === $off_day ) {
		return false;
	}

	if ( in_array( $now->format( 'Y-m-d' ), (array) $s['holidays'], true ) ) {
		return false;
	}

	$t = $now->format( 'H:i' );
	$start = $s['start'];
	$end   = $s['end'];

	if ( $start <= $end ) {
		return ( $t >= $start && $t < $end );
	}
	return ( $t >= $start || $t < $end ); // overnight window
}

/**
 * Expected role slug, or null when auto is off and no override is set.
 */
function aoh_expected_role( $s ) {
	$override = get_option( 'aoh_override', '' ); // '' | 'open' | 'closed'

	if ( 'open' === $override ) {
		return $s['day_role'];
	}
	if ( 'closed' === $override ) {
		return $s['night_role'];
	}
	if ( empty( $s['auto_enabled'] ) ) {
		return null;
	}
	return aoh_is_open( $s ) ? $s['day_role'] : $s['night_role'];
}

/**
 * Force target user's role to match the expected role (DB-level sync).
 */
function aoh_sync_target_role() {
	$s    = aoh_get_settings();
	$uid  = (int) $s['target_user'];
	if ( ! $uid ) {
		return;
	}
	$expected = aoh_expected_role( $s );
	if ( ! $expected ) {
		return;
	}
	$u = new WP_User( $uid );
	if ( ! $u->exists() ) {
		return;
	}
	$current = ! empty( $u->roles ) ? $u->roles[0] : '';
	if ( $current !== $expected ) {
		$u->set_role( $expected );
	}
}

/* ------------------------------------------------------- enforcement hooks */

/**
 * Runs on every request (REST / admin / front-end) once the user id is known,
 * BEFORE WP builds the current-user object. So the very first MCP request
 * after office hours already sees the locked role.
 */
function aoh_determine_current_user( $user_id ) {
	if ( ! $user_id ) {
		return $user_id;
	}
	$s = aoh_get_settings();
	if ( (int) $s['target_user'] !== (int) $user_id ) {
		return $user_id;
	}
	$expected = aoh_expected_role( $s );
	if ( ! $expected ) {
		return $user_id;
	}
	$u = new WP_User( $user_id );
	if ( $u->exists() && ( empty( $u->roles ) || $u->roles[0] !== $expected ) ) {
		$u->set_role( $expected );
	}
	return $user_id;
}
add_filter( 'determine_current_user', 'aoh_determine_current_user', 99 );

function aoh_schedule_cron() {
	if ( ! wp_next_scheduled( AOH_CRON_HOOK ) ) {
		wp_schedule_event( time() + MINUTE_IN_SECONDS, 'hourly', AOH_CRON_HOOK );
	}
}
add_action( 'init', 'aoh_schedule_cron' );
add_action( AOH_CRON_HOOK, 'aoh_sync_target_role' );

/* ------------------------------------------------------------- role build */

function aoh_install_roles() {
	if ( ! get_role( 'ai_night' ) ) {
		add_role( 'ai_night', 'AI Night (Locked)', array( 'read' => true ) );
	}
	aoh_rebuild_day_role();
}

function aoh_rebuild_day_role() {
	$s = aoh_get_settings();

	$editor = get_role( 'editor' );
	$caps   = $editor ? $editor->capabilities : array( 'read' => true );
	unset( $caps['unfiltered_html'] ); // scripts blocked at server level by default

	foreach ( aoh_extras() as $cap => $label ) {
		if ( ! empty( $s['extras'][ $cap ] ) ) {
			$caps[ $cap ] = true;
		} else {
			unset( $caps[ $cap ] );
		}
	}
	$caps['read'] = true;

	$role = get_role( 'ai_day' );
	if ( ! $role ) {
		add_role( 'ai_day', 'AI Day (Office Hours)', array_filter( $caps ) );
		return;
	}
	foreach ( array_keys( $role->capabilities ) as $c ) {
		$role->remove_cap( $c );
	}
	foreach ( $caps as $c => $v ) {
		if ( $v ) {
			$role->add_cap( $c );
		}
	}
}

/* ------------------------------------------------------------ admin pages */

function aoh_menu() {
	add_options_page(
		'AI Office Hours',
		'AI Office Hours',
		'manage_options',
		'ai-office-hours',
		'aoh_render_page'
	);
}
add_action( 'admin_menu', 'aoh_menu' );

function aoh_plugin_action_links( $links ) {
	$url = admin_url( 'options-general.php?page=ai-office-hours' );
	array_unshift( $links, '<a href="' . esc_url( $url ) . '">Settings</a>' );
	return $links;
}
add_filter( 'plugin_action_links_' . plugin_basename( __FILE__ ), 'aoh_plugin_action_links' );

function aoh_status_label( $s ) {
	$override = get_option( 'aoh_override', '' );
	if ( 'open' === $override ) {
		return '<span style="color:#008a20;font-weight:700;">FULL ACCESS (manual grant)</span>';
	}
	if ( 'closed' === $override ) {
		return '<span style="color:#b32d2e;font-weight:700;">LOCKED (manual revoke)</span>';
	}
	if ( empty( $s['auto_enabled'] ) ) {
		return '<span style="color:#996800;font-weight:700;">AUTO-OFF (role unchanged)</span>';
	}
	return aoh_is_open( $s )
		? '<span style="color:#008a20;font-weight:700;">FULL ACCESS (office hours)</span>'
		: '<span style="color:#b32d2e;font-weight:700;">LOCKED (outside office hours)</span>';
}

function aoh_render_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$s      = aoh_get_settings();
	$users  = get_users( array( 'orderby' => 'display_name', 'fields' => array( 'ID', 'display_name', 'user_login' ) ) );
	$roles  = wp_roles()->is_role( $s['day_role'] ) ? array_keys( wp_roles()->roles ) : array_keys( wp_roles()->roles );
	$target = $s['target_user'] ? get_userdata( $s['target_user'] ) : null;
	$day    = $target && ! empty( $target->roles ) ? $target->roles[0] : '-';
	$override = get_option( 'aoh_override', '' );
	?>
	<div class="wrap">
		<h1>AI Office Hours</h1>

		<div style="background:#fff;border:1px solid #c3c4c7;padding:15px 20px;margin:15px 0;max-width:820px;">
			<p style="margin-top:0;"><strong>Current status:</strong> <?php echo aoh_status_label( $s ); ?></p>
			<p style="margin-bottom:5px;">
				<strong>Target user:</strong> <?php echo $target ? esc_html( $target->user_login ) . ' (ID ' . (int) $target->ID . ')' : 'NOT SET'; ?>
				&nbsp;|&nbsp; <strong>Current role:</strong> <?php echo esc_html( $day ); ?>
				&nbsp;|&nbsp; <strong>Window:</strong> <?php echo esc_html( $s['start'] . ' - ' . $s['end'] ); ?>
				&nbsp;|&nbsp; <strong>Weekly off:</strong> <?php echo esc_html( aoh_off_day_label( $s['off_day'] ) ); ?>
			</p>
			<form method="post" style="margin-top:10px;">
				<?php wp_nonce_field( 'aoh_override', 'aoh_override_nonce' ); ?>
				<input type="hidden" name="aoh_override_action" value="x" />
				<button class="button button-primary" name="aoh_override" value="open" <?php disabled( 'open' === $override ); ?>>Grant access now</button>
				<button class="button" name="aoh_override" value="closed" <?php disabled( 'closed' === $override ); ?>>Revoke access now</button>
				<button class="button" name="aoh_override" value="" <?php disabled( '' === $override ); ?>>Resume auto schedule</button>
			</form>
		</div>

		<form method="post" action="options.php">
			<?php settings_fields( 'aoh_group' ); ?>
			<table class="form-table" role="presentation">
				<tr>
					<th scope="row">Auto switch</th>
					<td>
						<label>
							<input type="checkbox" name="aoh_settings[auto_enabled]" value="1" <?php checked( ! empty( $s['auto_enabled'] ) ); ?> />
							Enable office-hours auto switch (checked = auto)
						</label>
					</td>
				</tr>
				<tr>
					<th scope="row">Office window</th>
					<td>
						Start <input type="time" name="aoh_settings[start]" value="<?php echo esc_attr( $s['start'] ); ?>" required />
						End <input type="time" name="aoh_settings[end]" value="<?php echo esc_attr( $s['end'] ); ?>" required />
					</td>
				</tr>
				<tr>
					<th scope="row">Weekly off day</th>
					<td>
						<select name="aoh_settings[off_day]">
							<?php
							$days = array( -1 => 'No weekly off', 0 => 'Sunday', 1 => 'Monday', 2 => 'Tuesday', 3 => 'Wednesday', 4 => 'Thursday', 5 => 'Friday', 6 => 'Saturday' );
							foreach ( $days as $num => $label ) {
								printf(
									'<option value="%d" %s>%s</option>',
									(int) $num,
									selected( (int) $s['off_day'], (int) $num, false ),
									esc_html( $label )
								);
							}
							?>
						</select>
					</td>
				</tr>
				<tr>
					<th scope="row">Target user</th>
					<td>
						<select name="aoh_settings[target_user]">
							<?php
							foreach ( $users as $u ) {
								printf(
									'<option value="%d" %s>%s</option>',
									(int) $u->ID,
									selected( (int) $s['target_user'], (int) $u->ID, false ),
									esc_html( $u->display_name . ' (' . $u->user_login . ')' )
								);
							}
							?>
						</select>
						<p class="description">The ai-agent user. Its role is forced to match the schedule on every request.</p>
					</td>
				</tr>
				<tr>
					<th scope="row">Day role</th>
					<td>
						<select name="aoh_settings[day_role]">
							<?php foreach ( $roles as $r ) : ?>
								<option value="<?php echo esc_attr( $r ); ?>" <?php selected( $s['day_role'], $r ); ?>><?php echo esc_html( $r ); ?></option>
							<?php endforeach; ?>
						</select>
						&nbsp;&nbsp; Night role:
						<select name="aoh_settings[night_role]">
							<?php foreach ( $roles as $r ) : ?>
								<option value="<?php echo esc_attr( $r ); ?>" <?php selected( $s['night_role'], $r ); ?>><?php echo esc_html( $r ); ?></option>
							<?php endforeach; ?>
						</select>
					</td>
				</tr>
				<tr>
					<th scope="row">Day-role extra powers</th>
					<td>
						<?php foreach ( aoh_extras() as $cap => $label ) : ?>
							<label style="display:block;margin:4px 0;">
								<input type="checkbox" name="aoh_settings[extras][<?php echo esc_attr( $cap ); ?>]" value="1" <?php checked( ! empty( $s['extras'][ $cap ] ) ); ?> />
								<?php echo $label; ?>
							</label>
						<?php endforeach; ?>
						<p class="description">Tick/untick to modify the ai_day role instantly on Save. Base powers = Editor. File editing stays blocked if wp-config.php has <code>DISALLOW_FILE_EDIT</code>.</p>
					</td>
				</tr>
			</table>
			<?php submit_button( 'Save settings' ); ?>
		</form>

		<h2>Holidays (full-day lock)</h2>
		<div style="background:#fff;border:1px solid #c3c4c7;padding:15px 20px;max-width:820px;">
			<form method="post" style="margin-bottom:10px;">
				<?php wp_nonce_field( 'aoh_holiday', 'aoh_holiday_nonce' ); ?>
				<input type="date" name="aoh_holiday_date" required />
				<button class="button button-primary">Add holiday</button>
			</form>
			<?php if ( empty( $s['holidays'] ) ) : ?>
				<p style="margin:0;">No holidays added. Baaki off-days Weekly off se hote hain.</p>
			<?php else : ?>
				<ul style="margin:0;">
					<?php
					$sorted = (array) $s['holidays'];
					sort( $sorted );
					foreach ( $sorted as $d ) :
						?>
						<li style="margin:3px 0;">
							<?php echo esc_html( $d ); ?>
							<a href="<?php echo esc_url( wp_nonce_url( add_query_arg( array( 'page' => 'ai-office-hours', 'aoh_del_holiday' => $d ), admin_url( 'options-general.php' ) ), 'aoh_del_holiday_' . $d ) ); ?>" style="color:#b32d2e;">(remove)</a>
						</li>
					<?php endforeach; ?>
				</ul>
			<?php endif; ?>
			<p class="description">Naya holiday date add karo — us din din bhar locked rahega. Timezone: <?php echo esc_html( wp_timezone_string() ); ?></p>
		</div>
	</div>
	<?php
}

function aoh_off_day_label( $v ) {
	$days = array( -1 => 'None', 0 => 'Sunday', 1 => 'Monday', 2 => 'Tuesday', 3 => 'Wednesday', 4 => 'Thursday', 5 => 'Friday', 6 => 'Saturday' );
	$v    = (int) $v;
	return isset( $days[ $v ] ) ? $days[ $v ] : 'None';
}

/* ------------------------------------------------------------ save handlers */

function aoh_register_settings() {
	register_setting(
		'aoh_group',
		'aoh_settings',
		array(
			'type'              => 'array',
			'sanitize_callback' => 'aoh_sanitize_settings',
			'default'           => aoh_default_settings(),
		)
	);
}
add_action( 'admin_init', 'aoh_register_settings' );

function aoh_sanitize_settings( $in ) {
	$out = aoh_default_settings();

	$out['auto_enabled'] = empty( $in['auto_enabled'] ) ? 0 : 1;

	if ( isset( $in['start'] ) && preg_match( '/^\d{2}:\d{2}$/', $in['start'] ) ) {
		$out['start'] = $in['start'];
	}
	if ( isset( $in['end'] ) && preg_match( '/^\d{2}:\d{2}$/', $in['end'] ) ) {
		$out['end'] = $in['end'];
	}

	$out['off_day'] = isset( $in['off_day'] ) ? (string) (int) $in['off_day'] : '3';

	$old            = aoh_get_settings();
	$out['holidays'] = $old['holidays'];

	if ( isset( $in['target_user'] ) ) {
		$uid = (int) $in['target_user'];
		if ( $uid && get_userdata( $uid ) ) {
			$out['target_user'] = $uid;
		}
	}

	foreach ( array( 'day_role', 'night_role' ) as $key ) {
		if ( isset( $in[ $key ] ) && wp_roles()->is_role( sanitize_key( $in[ $key ] ) ) ) {
			$out[ $key ] = sanitize_key( $in[ $key ] );
		}
	}

	$out['extras'] = array();
	foreach ( aoh_extras() as $cap => $label ) {
		if ( ! empty( $in['extras'][ $cap ] ) ) {
			$out['extras'][ $cap ] = 1;
		}
	}

	// Reset manual override when schedule is saved, so auto takes over again.
	delete_option( 'aoh_override' );

	return $out;
}

// After settings save: rebuild day role + sync target user immediately.
add_action( 'update_option_aoh_settings', 'aoh_on_settings_saved' );
function aoh_on_settings_saved() {
	aoh_rebuild_day_role();
	aoh_sync_target_role();
}

/* --------------------------------------------- override / holiday handlers */

add_action( 'admin_init', 'aoh_handle_post_actions' );
function aoh_handle_post_actions() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$screen = isset( $_GET['page'] ) ? sanitize_key( wp_unslash( $_GET['page'] ) ) : '';

	// Grant / Revoke / Resume
	if ( isset( $_POST['aoh_override_action'] ) && 'ai-office-hours' === $screen ) {
		check_admin_referer( 'aoh_override', 'aoh_override_nonce' );
		$val = isset( $_POST['aoh_override'] ) ? sanitize_key( wp_unslash( $_POST['aoh_override'] ) ) : '';
		if ( in_array( $val, array( 'open', 'closed' ), true ) ) {
			update_option( 'aoh_override', $val );
		} else {
			delete_option( 'aoh_override' );
		}
		aoh_sync_target_role();
		wp_safe_redirect( add_query_arg( 'page', 'ai-office-hours', admin_url( 'options-general.php' ) ) );
		exit;
	}

	// Add holiday
	if ( isset( $_POST['aoh_holiday_date'] ) && 'ai-office-hours' === $screen ) {
		check_admin_referer( 'aoh_holiday', 'aoh_holiday_nonce' );
		$date = sanitize_text_field( wp_unslash( $_POST['aoh_holiday_date'] ) );
		if ( preg_match( '/^\d{4}-\d{2}-\d{2}$/', $date ) ) {
			$s         = aoh_get_settings();
			$s['holidays'] = array_values( array_unique( array_merge( $s['holidays'], array( $date ) ) ) );
			update_option( 'aoh_settings', $s );
			aoh_sync_target_role();
		}
		wp_safe_redirect( add_query_arg( 'page', 'ai-office-hours', admin_url( 'options-general.php' ) ) );
		exit;
	}

	// Remove holiday
	if ( isset( $_GET['aoh_del_holiday'] ) && 'ai-office-hours' === $screen ) {
		$date = sanitize_text_field( wp_unslash( $_GET['aoh_del_holiday'] ) );
		check_admin_referer( 'aoh_del_holiday_' . $date );
		$s            = aoh_get_settings();
		$s['holidays'] = array_values( array_diff( $s['holidays'], array( $date ) ) );
		update_option( 'aoh_settings', $s );
		aoh_sync_target_role();
		wp_safe_redirect( add_query_arg( 'page', 'ai-office-hours', admin_url( 'options-general.php' ) ) );
		exit;
	}
}

/* ---------------------------------------------------------- activation etc */

register_activation_hook( __FILE__, 'aoh_activate' );
function aoh_activate() {
	$s = get_option( 'aoh_settings', null );
	if ( null === $s || false === $s ) {
		$defaults            = aoh_default_settings();
		$agent               = get_user_by( 'login', 'ai-agent' );
		if ( $agent ) {
			$defaults['target_user'] = (int) $agent->ID;
		}
		update_option( 'aoh_settings', $defaults );
	}
	aoh_install_roles();
	aoh_schedule_cron();
	aoh_sync_target_role();
}

register_deactivation_hook( __FILE__, 'aoh_deactivate' );
function aoh_deactivate() {
	wp_clear_scheduled_hook( AOH_CRON_HOOK );
	// Role forced back to the scheduled one at deactivation time so the
	// account is never left in a stale elevated state.
	aoh_sync_target_role();
}
