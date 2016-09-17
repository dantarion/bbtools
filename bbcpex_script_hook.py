from __future__ import print_function
import frida
import sys
import atexit
def cleanup():
    global script
    script.unload()

session = frida.attach("BBCPEX.exe")
script = session.create_script("""
var cockpit_log = new NativeFunction(ptr("0x52B340"), 'void', ['int32','pointer']);
Interceptor.detachAll()
//Interceptor.attach(cockpit_log, function(args) {
//    send([args[0].toInt32(),args[1].toInt32(),args[2].toInt32()]);
//});
Interceptor.attach(ptr("0x4D4882"), function(args) {
    if(this.context.edi == 0)
    {
        var typePtr = Memory.readUInt(this.context.ecx);
        if(0x007D867C != typePtr)
            return;
        var index = Memory.readUInt(this.context.ecx.add(0x30));
        cockpit_log([0,1][index],this.context.esi.add(4));
        //send([Memory.readCString(this.context.esi.add(4)),this.context.ecx.toInt32().toString(16)])
        /*
        for (var i = 0; i < 0x3B; i++) {
            var p = 0x207E0478+ 52*i;
            var data = Memory.readUInt(ptr(p));
            var s = Memory.readCString(ptr(p+4));
            if(data != 0 || s != ""){
                send(["upon...",i,data.toString(16),s]);
            }
        }
        */
    }
    if(this.context.edi == 22031)
    {
        send(this.context.esi);
        this.context.edi = 0xFFFFF;
    }
});
""")

def on_message(message, data):
    print(message)
    #print("{1:X} {2} {3}".format(*message["payload"]))
script.on('message', on_message)
script.load()
print("loaded")
sys.stdin.read()
