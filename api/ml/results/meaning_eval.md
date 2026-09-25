# Meaning stage: LLM comparison

Prompt version 4. 13 synthetic messages (Hinglish, Roman Urdu, Arabizi, three-way mixes, 1 English control). *Register kept* = our language ID finds a non-English language the sender used in the reply to a mixed message (an echo of the message never counts). Our ID is still the rules baseline, so read the replies below too. *API errors* are provider failures (e.g. 503), not model output problems.

| Model | Answered | JSON errors | API errors | Median latency | Max latency | Register kept | Avg non-English share | Echoes |
|---|---|---|---|---|---|---|---|---|
| gemini-3.5-flash-lite | 13/13 | 0 | 0 | 0.92 s | 1.87 s | 12/12 | 0.55 | 0 |
| openai/gpt-oss-120b | 13/13 | 0 | 0 | 0.99 s | 1.34 s | 12/12 | 0.51 | 0 |
| gemini-3.1-flash-lite | 12/13 | 0 | 1 | 2.96 s | 8.22 s | 11/11 | 0.5 | 0 |
| openai/gpt-oss-20b | 13/13 | 0 | 0 | 0.81 s | 1.36 s | 12/12 | 0.47 | 0 |
| qwen/qwen3.8-27b | 13/13 | 0 | 0 | 0.68 s | 1.12 s | 12/12 | 0.44 | 0 |

## Replies

**yaar aaj office nahi aa paunga, tabiyat thodi kharab hai**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, apna khayal rakho aur rest karo  
  _Friend, I won't be able to come to the office today, my health is a bit bad._
- `openai/gpt-oss-120b`: take care yaar, jaldi theek ho ja, office ka kaam hum kar lenge  
  _Friend, I won't be able to come to the office today because I'm feeling a bit unwell._
- `gemini-3.1-flash-lite`: error ServerError 503
- `openai/gpt-oss-20b`: Arre yaar, thik ho ja, rest lo, jab theek ho jaoge milte hain  
  _Friend, I won’t be able to come to the office today because I’m feeling a bit unwell._
- `qwen/qwen3.8-27b`: chinta mat karo yaar, aaram karo aur subah theek hokar bata dena  
  _Buddy, I won't be able to come to the office today as I'm feeling a bit unwell._

**kal ka exam postpone ho gaya kya? mujhe kisi ne bataya nahi**

- `gemini-3.5-flash-lite`: haan yaar, kal ka exam postpone ho gaya hai, sab ko message aa gaya tha  
  _Did tomorrow's exam get postponed? Nobody told me._
- `openai/gpt-oss-120b`: na yaar, abhi confirm nahi hua, jaldi bata denge  
  _Did the exam get postponed? No one told me._
- `gemini-3.1-flash-lite`: haan bhai, official notice aa gaya hai, kal ka exam postpone ho gaya hai  
  _Did tomorrow's exam get postponed? No one told me._
- `openai/gpt-oss-20b`: haan, exam postpone ho gaya, next week ka schedule check kar le  
  _The exam was postponed, and no one told you about it._
- `qwen/qwen3.8-27b`: haan yaar exam postpone ho gaya, koi nahi bataya?  
  _Has yesterday's exam been postponed? No one told me._

**bhai ye laptop bohot slow chal raha hai, kya karun**

- `gemini-3.5-flash-lite`: bhai ek baar restart karke dekh, theek ho jayega  
  _Bro, this laptop is running very slow, what should I do?_
- `openai/gpt-oss-120b`: restart kar le, agar phir bhi slow ho to RAM clean kar ya service le lena  
  _Brother, this laptop is running very slowly, what should I do?_
- `gemini-3.1-flash-lite`: Bhai, ek baar restart karke dekho ya phir temp files clear kar lo, shayad sahi ho jaye.  
  _Brother, this laptop is running very slowly, what should I do?_
- `openai/gpt-oss-20b`: Arre bhai, restart karo, RAM check karo, and maybe uninstall recent apps.  
  _Your brother says the laptop is running very slow and asks what to do._
- `qwen/qwen3.8-27b`: bhai ek baar task manager check kar, agar zyada memory kha raha hai to kuch apps band kar de  
  _Bro, this laptop is running very slowly, what should I do?_

**didi mummy ne bola dinner pe jaldi aana, guests aa rahe hain**

- `gemini-3.5-flash-lite`: theek hai, main jaldi aa rahi hoon ghar!  
  _Older sister, mom said to come home early for dinner because guests are coming._
- `openai/gpt-oss-120b`: theek hai didi, jaldi aata hoon, guests ko milte hain  
  _Sister, Mom said to come early for dinner because guests are arriving._
- `gemini-3.1-flash-lite`: theek hai, main jaldi aa jaungi, dont worry.  
  _Sister, Mom said to come home early for dinner because guests are coming._
- `openai/gpt-oss-20b`: hmm, samajh gyi, jaldi aa jaungi  
  _Your sister says your mom told you to come early for dinner because guests are arriving._
- `qwen/qwen3.8-27b`: haan nanti, jaa jaldi aana, mummy ko gham nahi deti na  
  _Sister, mom said to come get ready for dinner quickly because the guests are here._

**yar meri flight delay ho gayi hai, pickup ke liye thora wait karna parega**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, main airport ke paas hi hoon, araam se aana  
  _Dude, my flight has been delayed, you'll have to wait a bit for the pickup._
- `openai/gpt-oss-120b`: no tension, thoda wait kar le, hum yahan hain  
  _Hey, my flight got delayed so I'll have to wait a bit for the pickup._
- `gemini-3.1-flash-lite`: koi masla nahi yar, tum araam se aao, main wait kar loonga  
  _My flight has been delayed, so you will have to wait a little while for the pickup._
- `openai/gpt-oss-20b`: thik hai, koi baat nahin, main wait karunga, thoda jaldi aata hun  
  _Hey, my flight got delayed, so I’ll need to wait a bit before the pickup._
- `qwen/qwen3.8-27b`: koi baat nahi yar, main wait karta hoon, reach hote hi bol dena  
  _Hey, my flight is delayed, so you will have to wait a bit longer for your pickup._

**aap ki baat theek hai lekin meri salary abhi tak nahi aayi**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, salary aate hi bata dena  
  _What you're saying is right, but my salary hasn't arrived yet._
- `openai/gpt-oss-120b`: samajh gaya, jaldi salary process kar dete hain  
  _I understand your point, but my salary hasn't arrived yet._
- `gemini-3.1-flash-lite`: oh, ye toh bohot tension ki baat hai, check kiya aapne ke kyun nahi aayi?  
  _Your point is valid, but I haven't received my salary yet._
- `openai/gpt-oss-20b`: Thik hai, payroll check kar leta hoon, jaldi aayega!  
  _You are right, but my salary hasn't come in yet._
- `qwen/qwen3.8-27b`: haan I know, lekin jaldi mil jayegi, tension mat lo  
  _You are right, but my salary has not arrived yet._

**kya scene hai weekend ka? beach chalein ya mall?**

- `gemini-3.5-flash-lite`: beach chalte hain yaar, weather bohot acha hai  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `openai/gpt-oss-120b`: beach chalenge, maza aayega, mall baad mein!  
  _What are the plans for the weekend? Should we go to the beach or the mall?_
- `gemini-3.1-flash-lite`: beach ka scene rakhte hain, weather acha hai!  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `openai/gpt-oss-20b`: kya scene hai, beach chalein? mall bhi theek hai  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `qwen/qwen3.8-27b`: bhai dono! pehle beach phir mall, full enjoy karna hai toh  
  _What's the plan for the weekend? Are we going to the beach or the mall?_

**habibi ana wa9alt, wainak? I'm at the main gate**

- `gemini-3.5-flash-lite`: ana jaay habibi, wait a second, main bas gate par hoon  
  _My love, I have arrived, where are you? I'm at the main gate._
- `openai/gpt-oss-120b`: habibi, yahan hoon, jaldi aao, main gate pe  
  _Habibi, I waited, where are you? I'm at the main gate._
- `gemini-3.1-flash-lite`: khalas habibi, ana jayi, wait for me bas 5 minutes.  
  _My dear, I have arrived. Where are you? I'm at the main gate._
- `openai/gpt-oss-20b`: yalla ana bhi wainak, gate ke paas hi hoon  
  _My friend, I'm here, where are you? I'm at the main gate._
- `qwen/qwen3.8-27b`: ya7ini hoon kol, main at the gate waiting for you habibi  
  _Darling, I arrived, where are you? I'm at the main gate._

**wallah el traffic kan kteer today, sorry ta2akhart**

- `gemini-3.5-flash-lite`: mish moshkila habibi, elhamdillah ala el salama  
  _I swear there was a lot of traffic today, sorry I'm late._
- `openai/gpt-oss-120b`: mafi mushkila, take care and see you soon  
  _I swear the traffic was heavy today, sorry I'm late._
- `gemini-3.1-flash-lite`: ma 3aleh habibi, koi baat nahi, bas pahunch jao safe rehna  
  _I swear the traffic was a lot today, sorry I am late._
- `openai/gpt-oss-20b`: afwan ya 7abibi, next time try avoid the rush  
  _I swear the traffic was really bad today, sorry I'm late._
- `qwen/qwen3.8-27b`: ahlan ta2akhart, mahmash, see you next time  
  _I swear the traffic was too much today, sorry for my late arrival._

**yalla guys, 3ndi meeting ba3d nus sa3a, call me later inshallah**

- `gemini-3.5-flash-lite`: tamam habibi, good luck with the meeting, call you baaden inshallah  
  _Come on guys, I have a meeting in half an hour, call me later God willing._
- `openai/gpt-oss-120b`: ok yalla, ba3d meeting call karte hain, inshallah  
  _Hey guys, I have a meeting in half an hour; call me later, God willing._
- `gemini-3.1-flash-lite`: tamam, good luck with the meeting, call karte hain baad mein inshallah  
  _Come on guys, I have a meeting in half an hour, call me later if God wills._
- `openai/gpt-oss-20b`: thik hai, baad mein call karna, inshallah  
  _Let's go guys, I have a meeting after half an hour, call me later God willing._
- `qwen/qwen3.8-27b`: yalla brother, ba3d meeting call you inshallah  
  _Hurry guys, I have a meeting in half an hour; call me later, God willing._

**bhai kal meeting hai, ana coming ba3d shwaya, traffic bohot hai**

- `gemini-3.5-flash-lite`: koi tension nahi bhai, araam se aao, main wait kar raha hoon  
  _Brother, there's a meeting tomorrow, I am coming a little later because there is a lot of traffic._
- `openai/gpt-oss-120b`: theek hai bhai, traffic ka tension mat lo, baad me milte hain  
  _Brother, there's a meeting tomorrow, I'll be coming a bit later because the traffic is heavy._
- `gemini-3.1-flash-lite`: koi baat nahi bhai, no tension, drive safe, meeting mein milte hain  
  _Brother, there is a meeting tomorrow, I am coming a little later, there is a lot of traffic._
- `openai/gpt-oss-20b`: bhai koi tension nahi, traffic ki wajah se late aao, milte hain  
  _Brother, there's a meeting tomorrow, I'll be coming a bit later, traffic is heavy._
- `qwen/qwen3.8-27b`: theek hai bhai, no tension, be safe  
  _Bro, there's a meeting tomorrow, I'll be coming right after a bit, the traffic is really heavy._

**khalas yaar, I'm done for today, kal baat karte hain inshallah**

- `gemini-3.5-flash-lite`: theek hai yaar, aram karo, kal milte hain inshallah  
  _Enough man, I'm done for today, let's talk tomorrow God willing._
- `openai/gpt-oss-120b`: thik hai yaar, kal baat karte hain, inshallah  
  _Okay buddy, I'm done for today; we'll talk tomorrow, God willing._
- `gemini-3.1-flash-lite`: theek hai yaar, rest karo, kal baat karte hain inshallah.  
  _Enough, my friend, I'm done for today, we'll talk tomorrow, God willing._
- `openai/gpt-oss-20b`: khalas bro, tomorrow baat karte hain, enjoy rest!  
  _Ok buddy, I'm finished for today, let's talk tomorrow God willing._
- `qwen/qwen3.8-27b`: chalo yaar, kal milte hain inshallah  
  _That's it, friend, I'm done for today, let's talk tomorrow inshallah._

**Can you send me the report before 5pm?**

- `gemini-3.5-flash-lite`: Sure, I will send it to you before 5pm.  
  _Can you send me the report before 5pm?_
- `openai/gpt-oss-120b`: Sure, I’ll get the report to you before 5 pm.  
  _The sender is asking if you can send the report before 5 pm._
- `gemini-3.1-flash-lite`: Sure, I will send it to you before 5pm.  
  _Can you please send me the report by 5 PM?_
- `openai/gpt-oss-20b`: Sure thing, I'll get it to you by 5pm.  
  _The sender is asking if you can send them the report before 5pm._
- `qwen/qwen3.8-27b`: Sure, I'll send it before 5.  
  _Please send me the report before 5:00 PM._
