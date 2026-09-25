# Meaning stage: LLM comparison

13 synthetic messages (Hinglish, Roman Urdu, Arabizi, three-way mixes, 1 English control). *Register kept* = our language ID finds Hindi/Urdu or Arabic in the reply to a mixed message. Our ID is still the rules baseline, so Arabizi replies without digits or seed words can be missed: read the replies below too.

| Model | Valid JSON | Median latency | Max latency | Register kept | Avg non-English share | Echoes |
|---|---|---|---|---|---|---|
| gemini-3.5-flash-lite | 13/13 | 0.98 s | 1.85 s | 12/12 | 0.55 | 0 |
| gemini-3.1-flash-lite | 11/13 | 2.57 s | 4.36 s | 10/10 | 0.48 | 0 |
| openai/gpt-oss-120b | 13/13 | 1.2 s | 1.84 s | 10/12 | 0.34 | 0 |
| openai/gpt-oss-20b | 13/13 | 0.83 s | 1.28 s | 12/12 | 0.53 | 1 |
| qwen/qwen3.8-27b | 13/13 | 0.77 s | 0.9 s | 12/12 | 0.53 | 0 |

## Replies

**yaar aaj office nahi aa paunga, tabiyat thodi kharab hai**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, apna khyal rakho aur aram karo  
  _Friend, I won't be able to come to the office today, my health is a bit bad._
- `gemini-3.1-flash-lite`: koi baat nahi yaar, rest karo aur apna khayal rakho, get well soon  
  _Friend, I won't be able to come to the office today, I'm feeling a bit unwell._
- `openai/gpt-oss-120b`: take care yaar, jaldi theek ho ja, office ka kaam baad me karte hain  
  _Friend, I won't be able to come to the office today because I'm feeling a bit unwell._
- `openai/gpt-oss-20b`: bura nahi, thik ho ja, kal milte hain  
  _Friend, I won't be able to come to the office today because I'm not feeling well._
- `qwen/qwen3.8-27b`: theek hai yaar, apna khayal rakhna, khairiyat puchi hoon  
  _Dude, I won't be able to come to the office today, I'm feeling a bit unwell._

**kal ka exam postpone ho gaya kya? mujhe kisi ne bataya nahi**

- `gemini-3.5-flash-lite`: haan yaar postpone ho gaya hai, tension mat lo  
  _Did tomorrow's exam get postponed? Nobody told me._
- `gemini-3.1-flash-lite`: haan yaar, kal ka exam postpone ho gaya hai, group pe notice check karo  
  _Has the exam tomorrow been postponed? No one told me._
- `openai/gpt-oss-120b`: nah yaar, postpone ho gaya, koi bataya hi nahi  
  _Did the exam get postponed? No one told me._
- `openai/gpt-oss-20b`: nahi pata, check with teacher  
  _Did the exam get postponed? I was told nothing._
- `qwen/qwen3.8-27b`: haan kal ka exam postpone ho gaya, koi bataya nahi tha  
  _Did yesterday's exam get postponed? Nobody told me._

**bhai ye laptop bohot slow chal raha hai, kya karun**

- `gemini-3.5-flash-lite`: bhai cache clear karke dekho, shayad fast chalne lagega  
  _Brother, this laptop is running very slow, what should I do?_
- `gemini-3.1-flash-lite`: bhai, ek baar restart karke dekho, shayad cache clear karne se theek ho jaye  
  _Brother, this laptop is running very slowly, what should I do?_
- `openai/gpt-oss-120b`: koi baat nahi bhai, pehle restart kar, agar phir bhi slow ho to cache clean kar ya memory upgrade kar  
  _Brother, this laptop is running very slow, what should I do?_
- `openai/gpt-oss-20b`: arre bhai, software updates check kar aur junk clean kar, bhala chalega  
  _Hey, my laptop is running very slow, what should I do?_
- `qwen/qwen3.8-27b`: bhai agli baar battery check karo ya cache clear karo, kal dekhta hain  
  _Bro, this laptop is running very slow, what should I do?_

**didi mummy ne bola dinner pe jaldi aana, guests aa rahe hain**

- `gemini-3.5-flash-lite`: theek hai didi, main jaldi aa jaungi dinner ke liye  
  _Sister, Mom said to come home early for dinner, guests are coming._
- `gemini-3.1-flash-lite`: error ServerError 503
- `openai/gpt-oss-120b`: theek hai didi, jaldi aata hoon, guests welcome hain  
  _Sister, Mom said to come early for dinner because guests are arriving._
- `openai/gpt-oss-20b`: thik hai, jaldi aa jata hun, guests ko welcome karte hain  
  _Sister, mom told us to come to dinner early, guests are arriving._
- `qwen/qwen3.8-27b`: haan didi, asde rahi hoon, aa raha hoon abhi  
  _Sister, mom said to come to dinner soon, the guests are here._

**yar meri flight delay ho gayi hai, pickup ke liye thora wait karna parega**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, main airport par thora wait kar lunga, message karna jab land ho  
  _Friend, my flight is delayed, you'll have to wait a little bit for the pickup._
- `gemini-3.1-flash-lite`: koi baat nahi yaar, tum aaram se flight se aao, main wait kar lunga.  
  _Friend, my flight has been delayed, you will have to wait a little for the pickup._
- `openai/gpt-oss-120b`: no tension yar, thoda wait kar lo, main jaldi aata hoon  
  _Friend, my flight is delayed, so we'll have to wait a bit for the pickup._
- `openai/gpt-oss-20b`: koi baat nahi, thoda rukna hi padega, sab thik hoga  
  _My flight has been delayed, so we’ll have to wait a bit for pickup._
- `qwen/qwen3.8-27b`: koi baat nahi yar, main wait kar raha hoon, tension mat lo  
  _Dude, my flight got delayed, you'll have to wait a little bit for the pickup._

**aap ki baat theek hai lekin meri salary abhi tak nahi aayi**

- `gemini-3.5-flash-lite`: koi baat nahi yaar, hopefully salary jaldi aa jayegi  
  _What you are saying is correct, but my salary hasn't arrived yet._
- `gemini-3.1-flash-lite`: bilkul theek, hopefully salary jald hi credit ho jayegi.  
  _Your point is valid, but my salary hasn't arrived yet._
- `openai/gpt-oss-120b`: haan, baat theek hai, lekin salary abhi tak aayi nahi, thoda patience rakhna  
  _You agree with the point but your salary hasn't arrived yet._
- `openai/gpt-oss-20b`: samajh gaya bro, salary abhi pending hai, check kar lein  
  _You are right but my salary hasn't arrived yet._
- `qwen/qwen3.8-27b`: haan theek hai, par boss se baat karo, abhi aana chahiye  
  _What you say is right, but my salary has not come yet._

**kya scene hai weekend ka? beach chalein ya mall?**

- `gemini-3.5-flash-lite`: scene set hai, beach hi chalte hain weekend pe!  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `gemini-3.1-flash-lite`: weekend scene sorted hai, beach hi chalte hain, bahut maza aayega!  
  _What is the plan for the weekend? Should we go to the beach or the mall?_
- `openai/gpt-oss-120b`: Got it, will follow the guidelines!  
  _The user provided instructions for handling mixed-language messages and gave examples._
- `openai/gpt-oss-20b`: kya scene hai? beach jaate hain, mall bhi dekhte hain!  
  _What's the plan for the weekend? Should we go to the beach or the mall?_
- `qwen/qwen3.8-27b`: beach chalein, mall boring hai  
  _What's up for the weekend? Should we go to the beach or the mall?_

**habibi ana wa9alt, wainak? I'm at the main gate**

- `gemini-3.5-flash-lite`: ana huna, main gate ke paas wait kar raha hoon, jaldi aao habibi!  
  _Darling, I have arrived, where are you? I'm at the main gate._
- `gemini-3.1-flash-lite`: ahlan habibi, main abhi gate ke paas aata hoon, bas 2 minutes ruk jao  
  _My friend, I have arrived, where are you? I'm at the main gate._
- `openai/gpt-oss-120b`: Got it! I'll keep the vibe and style just as you write it.  
  _I understand that you want me to interpret mixed-language messages and reply in the same style without correcting them._
- `openai/gpt-oss-20b`: 3tini update, gate hna.  
  _Habibi, I'm late, where are you? I'm at the main gate._
- `qwen/qwen3.8-27b`: ya ho wainak, main bhi aa rha hoon, wait karo shwaya  
  _Sweetheart, I've arrived, where are you? I'm at the main gate._

**wallah el traffic kan kteer today, sorry ta2akhart**

- `gemini-3.5-flash-lite`: maalesh habibi, mafi mushkilah, traffic kan kteer wallah, take your time  
  _I swear the traffic was a lot today, sorry I'm late._
- `gemini-3.1-flash-lite`: ma 3leesh habibi, traffic to roz ka hai, it is okay don't worry.  
  _I swear the traffic was very heavy today, sorry I am late._
- `openai/gpt-oss-120b`: Sure, I’ll translate and reply in the same mixed style you use!  
  _The user asks the assistant to translate mixed-language messages into plain English and provide a short, friendly reply in the same mixed style, without correcting the original writing style._
- `openai/gpt-oss-20b`: wallah traffic bohot tha, koi masla nahi, next time time pe milte hain  
  _I swear the traffic was crazy today, sorry I'm late._
- `qwen/qwen3.8-27b`: la taheress, traffic in sha Allah, billah ta2akhart no problem  
  _Honestly, the traffic was so heavy today, sorry for the late arrival._

**yalla guys, 3ndi meeting ba3d nus sa3a, call me later inshallah**

- `gemini-3.5-flash-lite`: tamam habibi, good luck with the meeting, talk to you later inshallah  
  _Come on guys, I have a meeting in half an hour, call me later God willing._
- `gemini-3.1-flash-lite`: error ServerError 503
- `openai/gpt-oss-120b` ⚠️ English: No message  
  _No message to process._
- `openai/gpt-oss-20b`: yalla guys, 3ndi meeting ba3d nus sa3a, call me later inshallah  
  _Hey guys, I have a meeting after half an hour, call me later God willing_
- `qwen/qwen3.8-27b`: yalla ba3d nus sa3a, call me later inshallah  
  _Alright guys, I'm at the meeting for over an hour, call me later if you want, God willing._

**bhai kal meeting hai, ana coming ba3d shwaya, traffic bohot hai**

- `gemini-3.5-flash-lite`: theek hai bhai, aram se aao, koi jaldi nahi hai  
  _Brother, there is a meeting tomorrow, I am coming a little later, there is a lot of traffic._
- `gemini-3.1-flash-lite`: koi baat nahi bhai, traffic toh bohot hai, tum araam se aao, no problem.  
  _Brother, there is a meeting tomorrow. I am coming a bit later, there is a lot of traffic._
- `openai/gpt-oss-120b` ⚠️ English:   
  __
- `openai/gpt-oss-20b`: thik hai bhai, traffic bohot hai, jaldi aaja.  
  _Brother, there's a meeting tomorrow, I’ll come a bit later because traffic is heavy._
- `qwen/qwen3.8-27b`: chalta hai bhai, late ho jana hoga, try to stay on time agar possible ho  
  _Bro, there is a meeting tomorrow; I'll be coming a bit late because there is a lot of traffic._

**khalas yaar, I'm done for today, kal baat karte hain inshallah**

- `gemini-3.5-flash-lite`: theek hai yaar, araam karo, kal baat karte hain inshallah  
  _Enough friend, I'm done for today, let's talk tomorrow God willing._
- `gemini-3.1-flash-lite`: theek hai yaar, rest karo, kal baat karenge inshallah.  
  _Enough friend, I'm done for today, let's talk tomorrow God willing._
- `openai/gpt-oss-120b`: ready yaar, bas message bhejo!  
  _Ready to help; just send a message._
- `openai/gpt-oss-20b`: khalas yaar, tomorrow milte hain, inshallah  
  _Enough friend, I'm done for today, let's talk tomorrow God willing._
- `qwen/qwen3.8-27b`: khalas hi, no tension, kal baat karte hain inshallah  
  _That's it, friend, I'm done for today, let's talk tomorrow God willing._

**Can you send me the report before 5pm?**

- `gemini-3.5-flash-lite`: Sure, I will send it before 5pm.  
  _Can you send me the report before 5pm?_
- `gemini-3.1-flash-lite`: Sure, I will send the report before 5pm.  
  _Can you send me the report before 5pm?_
- `openai/gpt-oss-120b`: Sure, I'll send it before 5pm.  
  _Can you send me the report before 5pm?_
- `openai/gpt-oss-20b`: Sure, I can send the report before 5pm.  
  _Sure, I can send the report before 5pm._
- `qwen/qwen3.8-27b` ⚠️ English: yes, I will send it to you before 5 pm  
  _Can you send me the report before 5 pm?_
