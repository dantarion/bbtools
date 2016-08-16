from __future__ import print_function
import frida
import sys
import atexit
def cleanup():
    global script
    script.unload()

session = frida.attach("BBCPEX.exe")
'''
script = session.create_script("""
Interceptor.detachAll()
Interceptor.attach(ptr("%s"), function(args) {
        var cmd = Memory.readUInt(args[0]);
        var message = "";
        if(cmd == 0)
            message = Memory.readCString(args[0].add(4));
        //if(cmd < 3 && cmd != 2)
        if(cmd == 2000)
        Memory.writeUint()
        if(message != "")
            send([args[0].toInt32(),this.context.ecx.toInt32(),Memory.readUInt(args[0]),message]);
});
""" % 0x4D4870)
'''
script = session.create_script("""
Interceptor.detachAll()
Interceptor.attach(ptr("%s"), function(args) {
    if(this.context.edi == 0)
            send(Memory.readCString(this.context.esi.add(4)))
    if(this.context.edi == 17001  )
    {
        this.context.edi = 0xFFFFF;
    }
});
""" % 0x4D4882)

def on_message(message, data):
    print(message["payload"])
    #print("{1:X} {2} {3}".format(*message["payload"]))
script.on('message', on_message)
script.load()
print("loaded")
sys.stdin.read()
