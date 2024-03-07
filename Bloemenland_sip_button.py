import pjsua as pj
import time
import threading

raspberry_pi = True

if raspberry_pi:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#pi register information
password = "Bloemenland2431a"
user = "1008"
domain = "192.168.0.36"

#to call information
to_user1 = "1006"
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

class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)
       

    def on_incoming_call(self, call):
        print("Incoming call from ", call.info().remote_uri)
        call.answer(200)
        print("Call is answered and hanging up!")
        call.hangup()

    def on_reg_state(self):
        if self.account.info().reg_status >= 200 and self.account.info().reg_status < 300:
            print("Registration successful")
        elif self.account.info().reg_status >= 400:
            print("Registration failed, retrying")
            time.sleep(10)
            self.lib.create_account(pj.AccountConfig(domain, user, password))

    def on_state(self):
        print("Call is ", self.account.info().state_text)
        if self.account.info().state == pj.CallState.CONFIRMED:
            print("Call is answered, hanging up")
            self.account.hangup()
            call_active = False
        if self.account.info().state == pj.CallState.DISCONNECTED:
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
        acc.set_callback(MyAccountCallback(acc))

        return acc
    
    except pj.Error as e:
        print("Exception: " + str(e))
        return False


def make_call(account, to_user):
    # Make the call
    call = account.make_call("sip:" + to_user + "@" + to_domain, MyAccountCallback())
    print("Call to " + to_user + " is made")

def long_press_function():
    print("Long press function")

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


#main function
while True:
    if raspberry_pi:
        input_state = GPIO.input(18)
        if input_state == False:
            if not call_active:
                # Record the time the button was pressed
                button_press_time = time.time()
                while GPIO.input(18) == False:
                    # Wait for the button to be released
                    time.sleep(0.1)
                # Calculate how long the button was pressed
                elapsed_time = time.time() - button_press_time
                # If the button was pressed for more than 2 seconds, call the long press function
                if elapsed_time > 10:
                    long_press_function()
                else:
                    # Otherwise, make a call
                    make_call(acc, to_user1)
                    call_active = True
            else:
                print("Call is active, cannot make another call")