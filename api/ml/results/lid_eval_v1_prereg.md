# Word-level language ID: first run (superseded)

> **Superseded; kept for transparency.** In this first run (1) macro-F1 wrongly counted labels absent from a test set as F1 = 0 (e.g. `ar` on LinCE), which deflated every macro number, and (2) the final model was fixed in advance as 'all sources'. Its ablation showed two sources without name labels (COMI-LINGUA, HingLID) hurting names and English, so the protocol was changed to select the training mix on validation data. Current results: [lid_eval.md](lid_eval.md).

Training data: comi (7678 sentences), haifa (2374 sentences), hinglid (3000 sentences), lince (4738 sentences), silver (592 sentences). CRF c1=0.2, c2=0.1 (chosen on a 10% slice of the training data). Model file: 2.8 MB, trained in 88.4 s.

Scores are over word tokens (punctuation, emoji and numbers are handled by the tokenizer, not the model). Macro-F1 averages en / hi-ur / ar / ne.

| Test set | Tokens | Rules accuracy | CRF accuracy | Rules macro-F1 | CRF macro-F1 |
|---|---|---|---|---|---|
| LinCE Hinglish dev | 13427 | 73.9% | 93.8% | 0.330 | 0.646 |
| Haifa Arabizi test | 2131 | 76.7% | 92.3% | 0.375 | 0.610 |
| COMI-LINGUA romanized test | 16664 | 47.7% | 92.0% | 0.256 | 0.461 |
| UAE hand-labelled | 312 | 80.1% | 95.8% | 0.611 | 0.861 |

## LinCE Hinglish dev: F1 per label

| Label | Support | Rules | CRF |
|---|---|---|---|
| en | 8901 | 0.837 | 0.970 |
| hi-ur | 3281 | 0.481 | 0.930 |
| ar | 0 | 0.000 | 0.000 |
| ne | 877 | 0.000 | 0.684 |

## Haifa Arabizi test: F1 per label

| Label | Support | Rules | CRF |
|---|---|---|---|
| en | 1289 | 0.843 | 0.963 |
| hi-ur | 0 | 0.000 | 0.000 |
| ar | 701 | 0.656 | 0.936 |
| ne | 97 | 0.000 | 0.542 |

## COMI-LINGUA romanized test: F1 per label

| Label | Support | Rules | CRF |
|---|---|---|---|
| en | 4031 | 0.483 | 0.886 |
| hi-ur | 10508 | 0.541 | 0.958 |
| ar | 0 | 0.000 | 0.000 |
| ne | 0 | 0.000 | 0.000 |

## UAE hand-labelled: F1 per label

| Label | Support | Rules | CRF |
|---|---|---|---|
| en | 122 | 0.797 | 0.971 |
| hi-ur | 140 | 0.814 | 0.965 |
| ar | 45 | 0.831 | 0.935 |
| ne | 5 | 0.000 | 0.571 |

## Ablation: macro-F1 when training on subsets of the sources

| Training data | Sentences | LinCE Hinglish dev | Haifa Arabizi test | COMI-LINGUA romanized test | UAE hand-labelled |
|---|---|---|---|---|---|
| LinCE only | 4738 | 0.688 | 0.430 | 0.430 | 0.609 |
| + Haifa Arabizi | 7112 | 0.685 | 0.608 | 0.432 | 0.807 |
| + Haifa + our silver | 7704 | 0.686 | 0.611 | 0.433 | 0.892 |
| All sources (final) | 18382 | 0.646 | 0.610 | 0.461 | 0.861 |

## UAE test set: accuracy by message type

| Type | Rules | CRF |
|---|---|---|
| hinglish | 80.8% | 96.8% |
| roman-urdu | 69.7% | 97.0% |
| arabizi | 77.3% | 95.5% |
| three-way | 82.7% | 94.2% |
| english | 100.0% | 94.1% |

## UAE test set: CRF errors

- the main problem is ki koi reply nahi karta: main (en→hi-ur)
- Rahul ne bola tha ki meeting baje hai: Rahul (ne→hi-ur)
- to phir kya plan hai weekend ka: to (hi-ur→en)
- kal Karachi ja raha hoon wapas Monday ko aaunga: Karachi (ne→hi-ur)
- bas thora sa wait karo main aa raha hoon: bas (hi-ur→ar)
- ana fel mall enta wein: mall (en→ar)
- yalla habibi the movie starts ba3d minutes: ba3d (ar→en)
- el traffic kteer 3al Sheikh Zayed road: road (ne→en)
- wallah bohot mushkil exam tha: bohot (hi-ur→ar), mushkil (hi-ur→ar)
- ana bhi aa raha hoon wait karo: ana (ar→hi-ur)
- The main gate is closed so use the side door: main (en→hi-ur)
- He said he will be late today: He (en→hi-ur)
