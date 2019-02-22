int LED_PIN = 5;
int COMMAND_PIN1 = 2;
int COMMAND_PIN2 = 3;

int brightness = 0;

int upordown = 0;
int tickcount = 0;

volatile int mode = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  pinMode(LED_PIN, OUTPUT);
  pinMode(COMMAND_PIN1, INPUT);
  pinMode(COMMAND_PIN2, INPUT);

  attachInterrupt(digitalPinToInterrupt(COMMAND_PIN1), changeLED_status, CHANGE);
  attachInterrupt(digitalPinToInterrupt(COMMAND_PIN2), changeLED_status, CHANGE);

  Serial.println("初期化完了");
}

void loop() {
  // put your main code here, to run repeatedly:

  switch(mode) {
    case 0: //消灯
      brightness = 0;
      break;
    case 1: //brink
      if(tickcount == 0){
        brightness = 255;
      }else if(tickcount == 100){
        brightness = 0;
      }else if(tickcount == 200){
        brightness = 255;
        tickcount = 0;
      }
      tickcount++;
      break;
    case 2: //breath
      if(upordown == 1){
        if(brightness < 255) brightness++;
        else upordown = 0;
      }else{
        if(brightness > 0) brightness--;
        else upordown = 1;
      }
      break;
    case 3: //定点灯
      brightness = 255;
      break;    
  }
  analogWrite(LED_PIN, brightness);
  //Serial.println(brightness);
  delay(1500/256);
  
}

void changeLED_status(){
  Serial.print("割り込み受信しました。");

  if((digitalRead(COMMAND_PIN1) == LOW) && (digitalRead(COMMAND_PIN2) == LOW)){
    mode = 3;
  }else if((digitalRead(COMMAND_PIN1) == LOW) && (digitalRead(COMMAND_PIN2) == HIGH)){
    mode = 2;
  }else if((digitalRead(COMMAND_PIN1) == HIGH) && (digitalRead(COMMAND_PIN2) == LOW)){
    mode = 1;
  }else if((digitalRead(COMMAND_PIN1) == HIGH) && (digitalRead(COMMAND_PIN2) == HIGH)){
    mode = 0;
  }
  Serial.print("mode");
  Serial.println(mode);
   
}

