#include <Arduino.h>

// Board header labels must be checked before wiring. All signal levels are 3.3 V.
constexpr int RADIO_RX=17, RADIO_TX=18, M0=4, M1=5, AUX=6;
HardwareSerial Radio(1);
String usbLine, radioLine;
unsigned long sentAt=0;
String pendingSeq;

uint16_t crc16(const String &s) {
  uint16_t crc=0xffff;
  for (size_t i=0;i<s.length();++i) {
    crc^=(uint16_t)(uint8_t)s[i]<<8;
    for (int j=0;j<8;++j) crc=(crc&0x8000)?(crc<<1)^0x1021:crc<<1;
  }
  return crc;
}
String frame(const String &body) {
  char tail[8];snprintf(tail,sizeof(tail),",%04X\n",crc16(body));
  return body+tail;
}
bool valid(const String &line, String &body) {
  int comma=line.lastIndexOf(',');
  if (comma<0 || line.length()-comma-1!=4) return false;
  body=line.substring(0,comma);
  String tail=line.substring(comma+1);
  for (size_t i=0;i<tail.length();++i) if (!isxdigit(tail[i])) return false;
  return crc16(body)==strtoul(tail.c_str(),nullptr,16);
}
bool ready(unsigned long timeout=2000) {
  unsigned long start=millis();
  while (!digitalRead(AUX)) {
    if (millis()-start>timeout) return false;
    delay(1);
  }
  delay(3);return true;
}
void receiveFrame(String line) {
  String body;
  if (!valid(line,body)) { Serial.println("ERR,CRC");return; }
  int a=body.indexOf(','), b=body.indexOf(',',a+1), c=body.indexOf(',',b+1);
  if (a<0 || b<0 || c<0) {Serial.println("ERR,FORMAT");return;}
#if ROLE_SENDER
  if (!body.startsWith("AK1,")) return;
  String seq=body.substring(a+1,b);
  Serial.printf("ACK,%s,%s,%s,%lu\n",seq.c_str(),body.substring(b+1,c).c_str(),body.substring(c+1).c_str(),millis()-sentAt);
#else
  if (!body.startsWith("NA1,")) return;
  int d=body.indexOf(',',c+1);
  if (d<0) {Serial.println("ERR,FORMAT");return;}
  Serial.println("RX,"+body.substring(a+1));
  if (!ready()) {Serial.println("ERR,AUX_TIMEOUT");return;}
  Radio.print(frame("AK1,"+body.substring(a+1,d)));
#endif
}
void command(String line) {
  if (line=="PING") {Serial.println(ROLE_SENDER?"READY,SENDER":"READY,RECEIVER");return;}
  if (line=="PARAMS") {
    // Query current radio registers in configuration mode.
    digitalWrite(M0,HIGH);digitalWrite(M1,HIGH);delay(100);
    if (!ready()) {Serial.println("ERR,AUX_TIMEOUT");digitalWrite(M0,LOW);digitalWrite(M1,LOW);return;}
    while(Radio.available()) Radio.read();
    uint8_t request[]={0xC1,0x00,0x09};Radio.write(request,3);Radio.flush();
    unsigned long start=millis();String dump;
    while(millis()-start<500) {
      if(Radio.available()) {char h[4];snprintf(h,sizeof(h),"%02X",Radio.read());dump+=h;}
      delay(1);
    }
    digitalWrite(M0,LOW);digitalWrite(M1,LOW);delay(100);
    Serial.println("PARAMS,"+dump);return;
  }
#if ROLE_SENDER
  if (!line.startsWith("SEND,")) {Serial.println("ERR,COMMAND");return;}
  String body="NA1,"+line.substring(5);
  String encoded=frame(body);
  if (encoded.length()>200) {Serial.println("ERR,FRAME_TOO_LONG");return;}
  if (!ready()) {Serial.println("ERR,AUX_TIMEOUT");return;}
  int comma=body.indexOf(',',4);
  pendingSeq=body.substring(4,comma);sentAt=millis();
  Radio.print(encoded);Radio.flush();
  Serial.printf("TX,%s,%u\n",pendingSeq.c_str(),(unsigned)encoded.length());
#else
  Serial.println("ERR,RECEIVER_ONLY");
#endif
}
void consume(Stream &s,String &buffer,bool usb) {
  while(s.available()) {
    char ch=s.read();
    if(ch=='\n') {if(usb)command(buffer);else receiveFrame(buffer);buffer="";}
    else if(ch!='\r') {
      buffer+=ch;
      if(buffer.length()>240) {buffer="";Serial.println("ERR,LINE_OVERFLOW");}
    }
  }
}
void setup() {
  pinMode(M0,OUTPUT);pinMode(M1,OUTPUT);pinMode(AUX,INPUT_PULLUP);
  digitalWrite(M0,LOW);digitalWrite(M1,LOW);
  Serial.begin(115200);Radio.begin(9600,SERIAL_8N1,RADIO_RX,RADIO_TX);
  delay(1000);
  Serial.println(ROLE_SENDER?"READY,SENDER":"READY,RECEIVER");
}
void loop() {consume(Serial,usbLine,true);consume(Radio,radioLine,false);delay(1);}
