# Word-level language ID: rules baseline vs trained CRF

**Selected model: + Haifa + silver + COMI-LINGUA** (15385 training sentences; CRF c1=0.2, c2=0.1; 2.2 MB; trained in 86.2 s). Available sentences per source: comi (7678), haifa (2374), hinglid (3000), lince (4738), silver (595).

Regularisation and the mix of training sources were chosen on validation data (10% of each human-labelled source), never on the test sets below. Scores are over word tokens (the tokenizer handles punctuation, emoji and numbers). Macro-F1 averages F1 over the labels en / hi-ur / ar / ne that occur in each test set; COMI-LINGUA has no name label, so its macro covers en / hi-ur only.

**History.** A first run fixed the final model in advance as 'all sources' and scored it on these test sets ([lid_eval_v1_prereg.md](lid_eval_v1_prereg.md)). Its ablation showed two sources without name labels hurting names, which is why this validation protocol and the 'without HingLID' candidate were added afterwards. So the test sets are not untouched. The pre-registered all-sources model scored 0.862 / 0.814 / 0.922 / 0.861 macro-F1 on LinCE / Haifa / COMI / UAE.

| Test set | Words | Rules accuracy | CRF accuracy | Rules macro-F1 | CRF macro-F1 |
|---|---|---|---|---|---|
| LinCE Hinglish dev | 13422 | 74.0% | 94.3% | 0.439 | 0.876 |
| Haifa Arabizi test | 2125 | 76.9% | 92.0% | 0.500 | 0.803 |
| COMI-LINGUA romanized test | 16664 | 47.7% | 92.1% | 0.512 | 0.924 |
| UAE hand-labelled | 361 | 79.8% | 94.5% | 0.611 | 0.877 |

## LinCE Hinglish dev: F1 per label

| Label | Words | Rules | CRF |
|---|---|---|---|
| en | 8901 | 0.838 | 0.974 |
| hi-ur | 3281 | 0.481 | 0.941 |
| ne | 877 | 0.000 | 0.714 |

## Haifa Arabizi test: F1 per label

| Label | Words | Rules | CRF |
|---|---|---|---|
| en | 1289 | 0.845 | 0.962 |
| ar | 701 | 0.656 | 0.931 |
| ne | 97 | 0.000 | 0.516 |

## COMI-LINGUA romanized test: F1 per label

| Label | Words | Rules | CRF |
|---|---|---|---|
| en | 4031 | 0.483 | 0.888 |
| hi-ur | 10508 | 0.541 | 0.960 |

## UAE hand-labelled: F1 per label

| Label | Words | Rules | CRF |
|---|---|---|---|
| en | 141 | 0.794 | 0.975 |
| hi-ur | 141 | 0.815 | 0.952 |
| ar | 70 | 0.833 | 0.915 |
| ne | 9 | 0.000 | 0.667 |

## Which training data helps: model selection on validation

Each candidate is trained on 90% of its sources. The **validation** column decided the selection; the test columns are shown only to explain what each source adds.

| Training data | Sentences | Validation macro-F1 | LinCE Hinglish dev | Haifa Arabizi test | COMI-LINGUA romanized test | UAE hand-labelled |
|---|---|---|---|---|---|---|
| LinCE only | 4264 | 0.800 | 0.918 | 0.583 | 0.864 | 0.607 |
| + Haifa Arabizi | 6400 | 0.876 | 0.914 | 0.802 | 0.866 | 0.852 |
| + Haifa + our silver | 6995 | 0.877 | 0.910 | 0.813 | 0.868 | 0.915 |
| + Haifa + silver + COMI-LINGUA ✅ | 13905 | 0.879 | 0.879 | 0.810 | 0.923 | 0.889 |
| All sources (+ HingLID) | 16905 | 0.873 | 0.867 | 0.809 | 0.921 | 0.895 |

## UAE test set: accuracy by message type

Small set (361 words, labelled by one team member): CRF accuracy 95% interval 92.2% to 96.5% (sentence bootstrap). Its macro-F1 rests on very few name tokens, so read accuracy and the language F1s instead. Silver training data was generated without showing these sentences to the LLM, and silver lines that contain one or share a 4-word phrase with one are removed.

| Type | Words | Rules | CRF |
|---|---|---|---|
| hinglish | 94 | 80.8% | 95.7% |
| roman-urdu | 66 | 69.7% | 98.5% |
| arabizi | 66 | 77.3% | 93.9% |
| three-way | 52 | 82.7% | 88.5% |
| gulf | 49 | 77.5% | 93.9% |
| english | 34 | 100.0% | 94.1% |

## UAE test set: every CRF error

- the main problem is ki koi reply nahi karta: main (en→hi-ur)
- mummy bol rahi thi ke tum late aaoge: mummy (en→hi-ur)
- Rahul ne bola tha ki meeting baje hai: Rahul (ne→hi-ur)
- to phir kya plan hai weekend ka: to (hi-ur→en)
- kal Karachi ja raha hoon wapas Monday ko aaunga: Karachi (ne→hi-ur)
- ana fel mall enta wein: mall (en→ne)
- 3ndi exam bukra need to study: 3ndi (ar→other)
- el traffic kteer 3al Sheikh Zayed road: road (ne→en)
- mashallah your Arabic is getting better: mashallah (ar→hi-ur)
- bhai ana coming ba3d shwaya traffic bohot hai: ana (ar→hi-ur)
- wallah bohot mushkil exam tha: wallah (ar→hi-ur)
- ana bhi aa raha hoon wait karo: ana (ar→hi-ur)
- shukran bhai you saved me today: shukran (ar→hi-ur)
- mafi mushkil kal milte hain: mafi (ar→hi-ur), mushkil (ar→hi-ur)
- chan zain if you told me before: chan (ar→ne), zain (ar→ne)
- yalla bhai 3'ada at Al Mallah: 3'ada (ar→other)
- The main gate is closed so use the side door: main (en→hi-ur)
- I have a bus to catch at six: to (en→hi-ur)
