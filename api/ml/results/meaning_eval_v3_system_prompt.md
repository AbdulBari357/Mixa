# Meaning stage: LLM comparison

13 synthetic messages (Hinglish, Roman Urdu, Arabizi, three-way mixes, 1 English control). *Register kept* = our language ID finds Hindi/Urdu or Arabic in the reply to a mixed message. Our ID is still the rules baseline, so Arabizi replies without digits or seed words can be missed: read the replies below too.

| Model | Valid JSON | Median latency | Max latency | Register kept | Avg non-English share | Echoes |
|---|---|---|---|---|---|---|
| gemini-3.5-flash-lite | 13/13 | 1.05 s | 2.34 s | 12/12 | 0.54 | 0 |
| gemini-3.1-flash-lite | 13/13 | 3.0 s | 5.42 s | 12/12 | 0.45 | 0 |
| openai/gpt-oss-120b | 13/13 | 1.0 s | 1.48 s | 12/12 | 0.53 | 0 |
| openai/gpt-oss-20b | 12/13 | 0.84 s | 1.58 s | 11/11 | 0.43 | 0 |
| qwen/qwen3.8-27b | 13/13 | 0.7 s | 1.53 s | 12/12 | 0.38 | 0 |

## Replies

**yaar aaj office nahi aa paunga, tabiyat thodi kharab hai**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, apna khyal rakho aur aram karo  
  _Mate, I won't be able to come to the office today, my health is a bit bad._
- `gemini-3.1-flash-lite`: koi baat nahi yaar, rest karo aur apna khayal rakho  
  _Buddy, I won't be able to come to the office today, my health is a bit down._
- `openai/gpt-oss-120b`: take care yaar, jaldi theek ho ja, kal office milte hain  
  _Friend, I won't be able to come to the office today, I'm feeling a bit unwell._
- `openai/gpt-oss-20b`: error HTTPStatusError 400
- `qwen/qwen3.8-27b`: khairi sandok, rest karo, main cover karta hoon  
  _Friend, I won't be able to come to the office today, I'm feeling a bit unwell._

**kal ka exam postpone ho gaya kya? mujhe kisi ne bataya nahi**

- `gemini-3.5-flash-lite`: haan yaar postpone ho gaya hai, group message check karo  
  _Did tomorrow's exam get postponed? Nobody told me._
- `gemini-3.1-flash-lite`: haan yaar notice abhi aya, exam postpone ho gaya hai, don't worry  
  _Has tomorrow's exam been postponed? No one told me._
- `openai/gpt-oss-120b`: nahin yaar, exam postpone ho gaya, koi tension mat lo  
  _Did the exam get postponed? Nobody told me._
- `openai/gpt-oss-20b`: nahin, exam postpone nahi hua, lekin tomorrow reschedule ho sakta hai  
  _The exam hasn't been postponed; you were just not informed, but it might be rescheduled tomorrow._
- `qwen/qwen3.8-27b`: haan yaar, abhi abhi news aayi, ek hafte baad hoga, tension mat lo  
  _Did yesterday's exam get postponed? No one told me._

**bhai ye laptop bohot slow chal raha hai, kya karun**

- `gemini-3.5-flash-lite`: ek baar restart karke dekh lo, shayad theek ho jaye  
  _Brother, this laptop is running very slow, what should I do?_
- `gemini-3.1-flash-lite`: bhai laptop restart karke dekho ya phr cache clear kar do, shayad thik ho jaye  
  _Brother, this laptop is running very slowly, what should I do?_
- `openai/gpt-oss-120b`: pehle restart kar, fir agar slow hi rahe to cache clear kar ya RAM upgrade kar, dekh lena  
  _Brother, this laptop is running very slow, what should I do?_
- `openai/gpt-oss-20b`: bhai, try rebooting the laptop, agar still slow ho to close background apps  
  _Brother, this laptop is running very slow, what should I do?_
- `qwen/qwen3.8-27b`: pehle task manager kholo aur background apps band karo, phir bhi slow ho toh malik se bolke dikhao  
  _Bro, this laptop is running very slow, what should I do?_

**didi mummy ne bola dinner pe jaldi aana, guests aa rahe hain**

- `gemini-3.5-flash-lite`: theek hai, main jaldi aa rahi hoon ghar  
  _Sister, mom said to come home early for dinner, guests are coming._
- `gemini-3.1-flash-lite`: theek hai, main jaldi aa jaungi, dont worry!  
  _Sister, Mom said to come home early for dinner, guests are coming._
- `openai/gpt-oss-120b`: theek hai didi, jaldi aata hoon, guests ke liye ready ho jao  
  _Sister, Mom said to come early for dinner because guests are arriving._
- `openai/gpt-oss-20b`: thik hai, jaldi aa jata hoon, sab ready kar leta hoon  
  _Your elder sister says that your mother told you to come to dinner early because guests are arriving._
- `qwen/qwen3.8-27b`: oky didi, main abhi aar rahi hoon, tension mat lo  
  _Sister, Mom said to come to dinner quickly, the guests are arriving._

**yar meri flight delay ho gayi hai, pickup ke liye thora wait karna parega**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, main airport pe hi hoon, aram se aao  
  _Friend, my flight has been delayed, you will have to wait a bit for the pickup._
- `gemini-3.1-flash-lite`: koi masla nahi yar, tum aram se ao, main wait kar lunga  
  _Buddy, my flight has been delayed, I will need to wait a little for the pickup._
- `openai/gpt-oss-120b`: theek hai, thoda wait kar lo, main aa jaunga  
  _Hey, my flight got delayed, so we'll have to wait a bit for the pickup._
- `openai/gpt-oss-20b`: no worries bhai, 30 min ke andar aayenge, thoda relax  
  _Hey, my flight got delayed; I’ll have to wait a bit for pickup._
- `qwen/qwen3.8-27b`: koi baat nahi, main wait karta hoon, tension mat lo  
  _Dude, my flight has been delayed, so you are going to have to wait a little bit for the pickup._

**aap ki baat theek hai lekin meri salary abhi tak nahi aayi**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, salary aate hi bata dena  
  _What you're saying is right, but my salary hasn't arrived yet._
- `gemini-3.1-flash-lite`: oh ho, tension na lo, shayad kl tak aa jaye gi salary.  
  _You are right, but my salary has not arrived yet._
- `openai/gpt-oss-120b`: samajh gaya, thoda patience rakh, salary jaldi aayegi, update milte hi bataunga  
  _You are right, but my salary hasn't arrived yet._
- `openai/gpt-oss-20b`: sahi kaha aap, salary check karte hain, thodi der mein aayegi  
  _Your point is right but my salary hasn't arrived yet._
- `qwen/qwen3.8-27b`: bhai koi baat nahi, thoda time lootega, mai ap se contact karta hoon  
  _What you are saying is correct, but my salary has not arrived yet._

**kya scene hai weekend ka? beach chalein ya mall?**

- `gemini-3.5-flash-lite`: beach chalte hain yaar, weather bohot acha hai  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `gemini-3.1-flash-lite`: beach ka scene best hai, chalo beach chalte hain!  
  _What's the scene for the weekend? Should we go to the beach or the mall?_
- `openai/gpt-oss-120b`: koi tension nahi, beach ya mall dono chalega, bas weather achha ho, decide kar lete hain  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `openai/gpt-oss-20b`: scene good, beach chalein? mall bhi thik hai  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `qwen/qwen3.8-27b`: beach chalein, jab ke mall me toh boring hota hai na  
  _What do you want to do this weekend? Shall we go to the beach or the mall?_

**habibi ana wa9alt, wainak? I'm at the main gate**

- `gemini-3.5-flash-lite`: ya akhi ana jay, wait for me 2 minutes at the gate  
  _Darling, I have arrived, where are you? I'm at the main gate_
- `gemini-3.1-flash-lite`: ahlan habibi, ana 2arib, just 5 minutes and I will be there.  
  _My dear, I have arrived, where are you? I'm at the main gate_
- `openai/gpt-oss-120b`: theek hai habibi, abhi aa raha hoon, milte hain wahan  
  _My dear, I am waiting, where are you? I'm at the main gate._
- `openai/gpt-oss-20b`: yahoo main gate se baat kar raha hu, abhi aaraha hu  
  _My dear, I have arrived, where are you? I'm at the main gate_
- `qwen/qwen3.8-27b`: ana barahe, mshi elak shwaya, standby!  
  _Hey darling, I've arrived, where are you? I'm at the main gate_

**wallah el traffic kan kteer today, sorry ta2akhart**

- `gemini-3.5-flash-lite`: mafi mushkila habibi, bas reach safely  
  _I swear there was a lot of traffic today, sorry I'm late_
- `gemini-3.1-flash-lite`: ma3lesh, no worries habibi, traffic toh roz ka scene hai  
  _I swear the traffic was a lot today, sorry I'm late._
- `openai/gpt-oss-120b`: no tension, wallah traffic kteer tha, next time on time milte hain  
  _I swear the traffic was a lot today, sorry I'm late._
- `openai/gpt-oss-20b`: koi baat nahi bro, next time traffic avoid karenge  
  _I swear the traffic was so heavy today, sorry I got stuck._
- `qwen/qwen3.8-27b`: khalas mahbi, no problem, just glad u made it  
  _Wallah, the traffic was so crazy today, sorry for being late._

**yalla guys, 3ndi meeting ba3d nus sa3a, call me later inshallah**

- `gemini-3.5-flash-lite`: tamam habibi, good luck with the meeting, baad mein baat karte hain!  
  _Come on guys, I have a meeting in half an hour, call me later God willing._
- `gemini-3.1-flash-lite`: okay, good luck with the meeting, talk to you ba3d!  
  _Come on guys, I have a meeting in half an hour, call me later God willing._
- `openai/gpt-oss-120b`: theek hai yalla, ba3d meeting call karte hain, inshallah  
  _Hey guys, I have a meeting in half an hour, call me later, God willing._
- `openai/gpt-oss-20b`: yalla, samajh aagya, baad mein call karenge, inshallah  
  _Let's go guys, I have a meeting after half an hour, call me later God willing._
- `qwen/qwen3.8-27b`: tamam habibi, basu noori shwaya 7at bakhoon  
  _Let's go everyone, I will have a meeting after half an hour, call me later inshallah._

**bhai kal meeting hai, ana coming ba3d shwaya, traffic bohot hai**

- `gemini-3.5-flash-lite`: koi baat nahi bhai,aram se aao, hum wait kar rahe hain  
  _Brother, there is a meeting tomorrow, I am coming a little later, there is a lot of traffic._
- `gemini-3.1-flash-lite`: koi masla nahi bhai, take your time, traffic bohot hai, araam se ana  
  _Brother, there is a meeting tomorrow. I am coming a little bit later, there is a lot of traffic._
- `openai/gpt-oss-120b`: no tension bhai, thoda late aao, meeting ke liye ready ho jao  
  _Bro, there's a meeting tomorrow, I'll be coming a bit later because the traffic is heavy._
- `openai/gpt-oss-20b`: theek hai bhai, traffic ka intezaar karna, milte hain ba3d shwaya  
  _Brother, there’s a meeting tomorrow, I’ll be coming a bit later, traffic is heavy._
- `qwen/qwen3.8-27b`: theek hai bhai, tension mat karo, late ho jaana kuch nahi hota  
  _Bro, we have a meeting tomorrow, I am coming a bit later, there is a lot of traffic_

**khalas yaar, I'm done for today, kal baat karte hain inshallah**

- `gemini-3.5-flash-lite`: theek hai yaar, aram karo, kal baat karte hain inshallah  
  _Enough man, I'm done for today, let's talk tomorrow God willing._
- `gemini-3.1-flash-lite`: theek hai yaar, aram karo, kal baat karte hain inshallah  
  _Okay friend, I'm done for today, let's talk tomorrow God willing._
- `openai/gpt-oss-120b`: thik hai yaar, aaj ka kaam khatam, kal baat karenge inshallah  
  _Okay friend, I'm done for today, let's talk tomorrow, God willing._
- `openai/gpt-oss-20b`: khalas yaar, shukriya, kal baat karte hain inshallah  
  _Enough, buddy, I’m finished for today, let’s talk tomorrow God willing._
- `qwen/qwen3.8-27b`: haan yaar rest kar lo, kal milte hain inshallah  
  _Enough, friend, I am finished for today, let's talk tomorrow, God willing_

**Can you send me the report before 5pm?**

- `gemini-3.5-flash-lite`: Sure, I will send it to you before 5pm.  
  _Can you send me the report before 5pm?_
- `gemini-3.1-flash-lite`: Sure, I will send the report before 5pm.  
  _Can you send me the report before 5 pm?_
- `openai/gpt-oss-120b`: Sure, I'll send it before 5pm.  
  _Can you send me the report before 5pm?_
- `openai/gpt-oss-20b`: Sure, I'll send it over by 5pm.  
  _Can you send me the report before 5pm?_
- `qwen/qwen3.8-27b`: Sure, I will send it by 5.  
  _Can you send me the report before 5pm?_
