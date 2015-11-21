// # Connection:
// #        M1 pin  -> Digital pin 4
// #        E1 pin  -> Digital pin 5
// #        M2 pin  -> Digital pin 7
// #        E2 pin  -> Digital pin 6
// #        Motor Power Supply -> Centor blue screw connector(5.08mm 3p connector)
// #        Motor A  ->  Screw terminal close to E1 driver pin
// #        Motor B  ->  Screw terminal close to E2 driver pin
// # 
// # Note: You should connect the GND pin from the DF-MD v1.3 to your MCU controller. They should share the GND pins.

int E1 = 6;
int M1 = 7;
int E2 = 3;                         
int M2 = 4;                           

//

String mCmdString = "";
boolean mCmdIsComplete = false;

//

class MotorActuator {
  
  public:

    void setup(int enablePin, int pwmPin, bool isInverted) {
        mEnablePin = enablePin;
        mPWMPin = pwmPin;
        mIsInverted = isInverted;
                
        pinMode(mEnablePin, OUTPUT);           
    }
    
    void setTargetSpeed(int targetSpeed) { 

      if (targetSpeed > 0) { 
        mTargetSpeed = targetSpeed;
        digitalWrite(mEnablePin, HIGH);       
      }
      else {        
        mTargetSpeed = -targetSpeed;
        digitalWrite(mEnablePin, LOW);       
      }

      mCurrentSpeed = mTargetSpeed;
      
      if (mIsInverted) {
        mCurrentSpeed *= -1;
      }
      
      analogWrite(mPWMPin, mCurrentSpeed);
    }
    
 protected:
    int mEnablePin;
    int mPWMPin;
    bool mIsInverted;
    int mTargetSpeed;
    int mCurrentSpeed;
};

//

void processCommands() {

  while (Serial.available()) {
    
    char inChar = (char)Serial.read();

    if (inChar == '\n' || inChar == '0') {
      mCmdString.trim();
      mCmdIsComplete = true;
    }
    else {    
      mCmdString += inChar;
    }
  }
}

//

MotorActuator m1;
MotorActuator m2;

//

void setup() 
{ 
  Serial.begin(9600);           // set up Serial library at 9600 bps
  
  m1.setup(M1, E1, false);
  m2.setup(M2, E2, false);
} 

//

void processCommand(String cmd) {

  Serial.println(cmd);
  
  if (cmd.equals("FWD")) {
    m1.setTargetSpeed(255);
    m2.setTargetSpeed(255);    
  }
  else if (cmd == "BACK") {
    m1.setTargetSpeed(-255);
    m2.setTargetSpeed(-255);        
  }
  else if (cmd == "LEFT") {
    m1.setTargetSpeed(255);
    m2.setTargetSpeed(-255);            
  }
  else if (cmd == "RIGHT") {
    m1.setTargetSpeed(-255);
    m2.setTargetSpeed(255);            
  }
  else if (cmd == "STOP") {
    m1.setTargetSpeed(0);
    m2.setTargetSpeed(0);            
  }
}

//

void loop() 
{ 
  processCommands();

  if (mCmdIsComplete) {
    processCommand(mCmdString);
    mCmdIsComplete = false;  
    mCmdString = "";  
  }  
}
