/*
 * Copyright 2016 Jiří Janoušek <janousek.jiri@gmail.com>
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
#if FLATPAK
 const string FLATPAK_ARCHIVE = "/app/share/nuvolaplayer3/web_apps/" + APP_ID + ".tar.gz";
#endif


MainLoop loop = null;
int retcode = 0;
CommandLine cmd_line = null;
StringBuilder stdout_buf = null;
StringBuilder stderr_buf = null;

[DBus (name="org.gtk.private.CommandLine")]
public class CommandLine : GLib.Object
{
	public CommandLine()
	{
		 stdout_buf = new StringBuilder("");
		 stderr_buf = new StringBuilder("");
	}
	
	public void print(string text)
	{
		stdout.puts(text);
		stdout_buf.append(text);
	}
	
	public void print_error(string text)
	{
		stderr.puts(text);
		stderr_buf.append(text);
	}
}

private async void launch(Variant args) throws GLib.Error
{
	var conn = yield Bus.@get(BusType.SESSION, null);
	cmd_line = new CommandLine();
	var cmd_line_path = "/eu/tiliado/NuvolaSdk/CommandLine";
	conn.register_object<CommandLine>(cmd_line_path, cmd_line);
	var app_proxy = yield DBusProxy.@new(
		conn, DBusProxyFlags.DO_NOT_LOAD_PROPERTIES|DBusProxyFlags.DO_NOT_CONNECT_SIGNALS, null,
		"eu.tiliado.Nuvola", "/eu/tiliado/Nuvola", "org.gtk.Application", null);
	var platform = new VariantBuilder(new VariantType("a{sv}"));
	platform.add("{sv}", "cwd", new Variant.bytestring(Environment.get_current_dir()));
	platform.add("{sv}", "desktop-startup-id", new Variant.string("0"));
	var params = new Variant("(o@aaya{sv})", cmd_line_path, args, platform);
	var result = yield app_proxy.call("CommandLine", params, 0, -1, null);
	result.get("(i)", out retcode);
}

int main(string[] argv)
{
	#if FLATPAK
		for (var i = 1; i < argv.length; i++)
			if (argv[i] == "--data")
				return launch_data_provider();
	#endif
	var builder = new VariantBuilder(new VariantType("aay"));
	builder.add_value(new Variant.bytestring(argv[0]));
	builder.add_value(new Variant.bytestring("-a"));
	builder.add_value(new Variant.bytestring(APP_ID));
	for (var i = 1; i < argv.length; i++)
		builder.add_value(new Variant.bytestring(argv[i]));
	var args = builder.end();
	loop = new MainLoop();
	launch.begin(args, on_launch_done);
	loop.run();
	return retcode;
}

private void on_launch_done(GLib.Object? o, AsyncResult res)
{
	try
	{
		launch.end(res);
		if (retcode != 0)
			show_error("Return code %d".printf(retcode));
	}
	catch (GLib.Error e)
	{
		show_error(e.message);
	}
	quit();
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
