import pjsua as pj
import time
import threading



import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#pi register information
password = "Bloemenland2431a"
user = "1008"
domain = "192.168.0.36"

#to call information
to_user1 = "1002"
to_user2 = "1006"
to_domain = "192.168.0.36"

# Create a library instance
lib = pj.Lib()

#active call flag
call_active = False

def check_registration_status(account):
     # Register the thread with PJSIP
    pj.Lib.instance().thread_register("check_registration_status")

    # Check the registration status and try to re-register if necessary
    status = account.info().reg_status
    if status >= 200 and status < 300:
        print("Account is registered, status is ", status)
    elif status >= 400:
        print("Account registration failed, retrying...")
        acc = lib.create_account(pj.AccountConfig(domain, user, password))
        time.sleep(10)
    else:
        print("Account registration is in progress, status is ", status)

    # Reset the timer
    timer = threading.Timer(30.0, check_registration_status, args=[account])
    timer.start()


class MyCallCallback(pj.CallCallback):
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)
        self.player_id = None

    def _set_account(self, account):
        self.account = account

    def on_mwi_info(self, body):
        pass

    def is_call_active(self):
        return self.call.info().state == pj.CallState.CONFIRMED

    def on_incoming_call(self, call):
        print("Incoming call from ", self.call.info().remote_uri)
        self.call.answer(200)

    def on_reg_state(self):
        if self.account.info().reg_status >= 200 and self.account.info().reg_status < 300:
            print("Registration successful")
        elif self.account.info().reg_status >= 400:
            print("Registration failed, retrying")
            time.sleep(10)
            self.lib.create_account(pj.AccountConfig(domain, user, password))

    def on_state(self):
        global call_active
        print("Call is ", self.call.info().state_text)
        if self.call.info().state == pj.CallState.CONFIRMED:
            print("Call is answered, hanging up")
            self.call.hangup()
            call_active = False
        if self.call.info().state == pj.CallState.DISCONNECTED:
            print("Call is disconnected")
            call_active = False
  



def first_registration():
    try:
        # Initialize the library
        lib.init()

        # Create a transport instance
        transport = lib.create_transport(pj.TransportType.UDP)

        # Start the library
        lib.start()

        # Create and register an account
        acc = lib.create_account(pj.AccountConfig(domain, user, password))
        acc.set_callback(MyCallCallback(acc))

        return acc
    
    except pj.Error as e:
        print("Exception: " + str(e))
        return False


def make_call(account, to_user):
    # Make the call
    call = account.make_call("sip:" + to_user + "@" + to_domain, MyCallCallback())
    print("Call to " + to_user + " is made")

#setup
# Register the thread with PJSIP
acc = first_registration()
# Check the registration status and try to re-register if necessary
while acc == False:
    print("Retrying registration")
    acc = first_registration()
    time.sleep(15)
# Reset the timer for checking registration status
timer = threading.Timer(30.0, check_registration_status, args=[acc])
timer.start()

while acc.info().reg_status < 200 or acc.info().reg_status >= 300:
    print("Waiting for registration")
    time.sleep(1)

while True:
    input_state = GPIO.input(4)
    if input_state == False:
        #register button press and time
        print("Button pressed" + time.strftime("%Y-%m-%d %H:%M:%S")) 
        while GPIO.input(4) == False:
            time.sleep(0.5)
        if not call_active:
            call_active = True
            make_call(acc, to_user1)
            
        else:
            print("Call is active, cannot make another call")