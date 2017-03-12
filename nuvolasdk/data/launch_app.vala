/*
 * Copyright 2016-2017 Jiří Janoušek <janousek.jiri@gmail.com>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met: 
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer. 
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution. 
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

namespace Nuvolasdk
{

extern const string APP_ID;
extern const string UNIQUE_ID;
extern const bool FLATPAK_BUILD;
extern const string NUVOLA_BUS;
#if FLATPAK
 const string FLATPAK_ARCHIVE = "/app/share/nuvolaplayer3/web_apps/" + APP_ID + ".tar.gz";
#endif


struct Args
{
	static bool debug;
	#if FLATPAK
	static bool data;
	#endif
	static bool verbose;
	static bool version;
	static string? log_file;
	
	public const OptionEntry[] options =
	{
		{ "verbose", 'v', 0, OptionArg.NONE, ref Args.verbose, "Print informational messages", null },
		#if FLATPAK
		{ "data", 0, 0, OptionArg.NONE, ref Args.data, "Launch data provider", null },
		#endif
		{ "debug", 'D', 0, OptionArg.NONE, ref Args.debug, "Print debugging messages", null },
		{ "version", 'V', 0, OptionArg.NONE, ref Args.version, "Print version and exit", null },
		{ "log-file", 'L', 0, OptionArg.FILENAME, ref Args.log_file, "Log to file", "FILE" },
		{ null }
	};
}


MainLoop loop = null;
int retcode = 0;
StringBuilder stdout_buf = null;
StringBuilder stderr_buf = null;

int main(string[] argv)
{
	try
	{
		var opt_context = new OptionContext("- %s".printf(Nuvola.get_app_name()));
		opt_context.set_help_enabled(true);
		opt_context.add_main_entries(Args.options, null);
		opt_context.set_ignore_unknown_options(true);  // e.g. --gapplication-service
		opt_context.parse(ref argv);
	}
	catch (OptionError e)
	{
		stderr.printf("option parsing failed: %s\n", e.message);
		return 1;
	}
	
	if (Args.version)
	{
		stdout.printf("%s %s\n", Nuvola.get_app_name(), Nuvola.get_version());
		return 0;
	}
	
	#if FLATPAK
	if (Args.data)
		return launch_data_provider();
	#endif
	
	FileStream? log = null;
	if (Args.log_file != null)
	{
		log = FileStream.open(Args.log_file, "w");
		if (log == null)
		{
			stderr.printf("Cannot open log file '%s' for writting.\n", Args.log_file);
			return 1;
		}
	}
	
	
	Diorite.Logger.init(log != null ? log : stderr, Args.debug ? GLib.LogLevelFlags.LEVEL_DEBUG
	  : (Args.verbose ? GLib.LogLevelFlags.LEVEL_INFO: GLib.LogLevelFlags.LEVEL_WARNING),
	  true, "Runner");
	
	// Init GTK early to have be able to use Gtk.IconTheme stuff
	string[] empty_argv = {};
	unowned string[] unowned_empty_argv = empty_argv;
	Gtk.init(ref unowned_empty_argv);
	
	var storage = new Diorite.XdgStorage.for_project(Nuvola.get_app_id());
	var web_apps_storage = storage.get_child("web_apps");
	var web_app_reg = new Nuvola.WebAppRegistry(web_apps_storage.user_data_dir, web_apps_storage.data_dirs, true, null);
	var web_app = web_app_reg.get_app_meta(APP_ID);
	if (web_app == null)
	{
		show_error("App %s not found.".printf(APP_ID));
		return 2;
	}
	#if !FLATPAK
	if (!web_app.has_desktop_launcher)
	{
		warning(
			"The %s script doesn't provide a desktop file. It might not function properly."
			+ " Ask the maintainer to switch to the Nuvola SDK "
			+ "<https://github.com/tiliado/nuvolasdk> and build it with `./configure --with-desktop-launcher`.",
			web_app.name);
	}
	#endif
	var app_storage = new Nuvola.WebAppStorage(
	  storage.user_config_dir.get_child(Nuvola.WEB_APP_DATA_DIR).get_child(web_app.id),
	  storage.user_data_dir.get_child(Nuvola.WEB_APP_DATA_DIR).get_child(web_app.id),
	  storage.user_cache_dir.get_child(Nuvola.WEB_APP_DATA_DIR).get_child(web_app.id));
	
	var controller = new Nuvola.AppRunnerController(storage, web_app, app_storage, null, NUVOLA_BUS);
	return controller.run(argv);
}


void quit()
{
	Idle.add(() => {loop.quit(); return false;});
}


private void show_error(string error)
{
	stderr.printf("%s\n", error);
	string[] _args = {};
	unowned string[] args = _args;
	Gtk.init(ref args);
	var window = new Gtk.Window();
	window.set_default_size(250, -1);
	var grid = new Gtk.Grid();
	grid.margin = 15;
	grid.row_spacing = 15;
	window.add(grid);
	var text = "Failed to launch the application.";
	#if FLATPAK
		text +="\n\nIs the eu.tiliado.Nuvola flatpak installed?";
	#endif
	var label = new Gtk.Label(text);
	label.set_line_wrap(true);
	label.selectable = true;
	grid.add(label);
	grid.orientation = Gtk.Orientation.VERTICAL;
	var text_view = new Gtk.TextView();
	grid.add(text_view);
	text_view.editable = false;
	text_view.hexpand = true;
	text_view.wrap_mode = Gtk.WrapMode.WORD_CHAR;
	var buffer = text_view.buffer;
	buffer.insert_at_cursor(error, -1);
	buffer.insert_at_cursor("\n", -1);
	if (stdout_buf != null && stdout_buf.len > 0)
	{
		buffer.insert_at_cursor(stdout_buf.str, (int) stdout_buf.len);
		buffer.insert_at_cursor("\n", -1);
	}
	if (stderr_buf != null && stderr_buf.len > 0)
	{
		buffer.insert_at_cursor(stderr_buf.str, (int) stderr_buf.len);
		buffer.insert_at_cursor("\n", -1);
	}
	window.delete_event.connect((e) => {Gtk.main_quit(); return false;});
	window.show_all();
	label.select_region(0, 0);
	Gtk.main();
}

#if FLATPAK
int64 quit_time = 0;
int n_fd_opened = 0;


private bool provider_quit_cb()
{
	if (n_fd_opened == 0 && GLib.get_monotonic_time() > quit_time)
	{
		quit_time = -1;
		quit();
		return false; // cancel
	}
	return true; // continue
}


private int launch_data_provider()
{
	loop = new MainLoop();
	quit_time = GLib.get_monotonic_time() + 10 * 1000000;
	Bus.own_name(
		BusType.SESSION, UNIQUE_ID + ".data", BusNameOwnerFlags.NONE,
		on_bus_aquired,
		() => {},
		() => {stderr.printf("Could not acquire name\n"); retcode = 1; quit();}
	);
	Timeout.add_seconds(1, provider_quit_cb);
	loop.run();
	return retcode;
}


void on_bus_aquired (DBusConnection conn)
{
    try
    {
        conn.register_object("/eu/tiliado/Nuvola/DataProvider", new DataProvider(FLATPAK_ARCHIVE));
    }
    catch (IOError e)
    {
        stderr.printf ("Could not register service\n");
        retcode = 1;
        quit();
    }
}


[DBus (name="eu.tiliado.Nuvola.DataProvider")]
public class DataProvider: GLib.Object
{
	private string archive_path;
	
	public DataProvider(string archive_path)
	{
		this.archive_path = archive_path;
	}
	
	public bool get_data_stream(out GLib.UnixInputStream? input_stream)
	{
		input_stream = null;
		if (quit_time < 1)
			return false;
		quit_time = GLib.get_monotonic_time() + 15 * 1000000;
		
		var fd = new InputFd(archive_path);
		if (fd.unix_stream != null)
		{
			input_stream = fd.unix_stream;
			n_fd_opened++;
			Timeout.add_seconds(15, fd.close_cb);
			return true;
		}
		return false;
	}
}


public class InputFd
{
	public FileStream? stream;
	public UnixInputStream? unix_stream = null;
	
	public InputFd(string path)
	{
		stream = FileStream.open(path, "r");
		if (stream != null)
			unix_stream = new UnixInputStream(stream.fileno(), false);
	}
	
	public bool close_cb()
	{
		stream = null;
		n_fd_opened--;
		return false;
	}
}
#endif

}
