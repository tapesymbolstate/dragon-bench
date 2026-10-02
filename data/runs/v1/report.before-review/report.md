# Dragon Bench report

Stems: en `Dragon is`, ko `용은`, zh `龙是`, ja `竜は`

## Filtering funnel

| model | lang | n | same language | dragon sense | clarification | multi_sense | definition | completion | net valence | eastern / western / general |
|---|---|---|---|---|---|---|---|---|---|---|
| gpt-6-luna | en | 100 | 100 | 93 | 73 | 13 | 14 | 0 | +0.08 | 10 / 1 / 212 |
| gpt-6-luna | ko | 100 | 100 | 80 | 44 | 40 | 16 | 0 | +0.21 | 76 / 27 / 118 |
| gpt-6-luna | zh | 100 | 100 | 95 | 93 | 3 | 4 | 0 | +0.62 | 225 / 8 / 63 |
| gpt-6-luna | ja | 100 | 100 | 74 | 38 | 0 | 55 | 7 | +0.11 | 71 / 57 / 149 |
| claude-haiku-4.5 | en | 100 | 100 | 100 | 2 | 53 | 45 | 0 | +0.18 | 225 / 193 / 844 |
| claude-haiku-4.5 | ko | 100 | 100 | 100 | 21 | 27 | 52 | 0 | +0.45 | 570 / 32 / 293 |
| claude-haiku-4.5 | zh | 100 | 100 | 100 | 0 | 29 | 71 | 0 | +0.55 | 1009 / 13 / 157 |
| claude-haiku-4.5 | ja | 100 | 100 | 100 | 12 | 41 | 43 | 4 | +0.47 | 438 / 32 / 456 |
| gemini-3.5-flash-lite | en | 100 | 100 | 100 | 3 | 73 | 21 | 3 | +0.09 | 304 / 308 / 433 |
| gemini-3.5-flash-lite | ko | 100 | 100 | 100 | 9 | 34 | 57 | 0 | +0.23 | 428 / 342 / 303 |
| gemini-3.5-flash-lite | zh | 100 | 100 | 100 | 1 | 5 | 94 | 0 | +0.13 | 1444 / 26 / 85 |
| gemini-3.5-flash-lite | ja | 100 | 100 | 100 | 2 | 9 | 89 | 0 | +0.20 | 753 / 375 / 188 |
| llama-4-maverick | en | 100 | 100 | 100 | 5 | 4 | 90 | 1 | +0.24 | 159 / 114 / 944 |
| llama-4-maverick | ko | 100 | 82 | 77 | 12 | 4 | 78 | 3 | +0.27 | 324 / 87 / 324 |
| llama-4-maverick | zh | 100 | 100 | 100 | 4 | 0 | 96 | 0 | +0.23 | 143 / 60 / 873 |
| llama-4-maverick | ja | 100 | 100 | 100 | 0 | 0 | 100 | 0 | +0.18 | 178 / 130 / 539 |
| mistral-small-2603 | en | 97 | 97 | 87 | 53 | 14 | 25 | 4 | +0.11 | 129 / 101 / 424 |
| mistral-small-2603 | ko | 97 | 94 | 93 | 4 | 22 | 71 | 0 | +0.44 | 654 / 16 / 181 |
| mistral-small-2603 | zh | 100 | 100 | 99 | 6 | 0 | 93 | 0 | +0.42 | 997 / 22 / 90 |
| mistral-small-2603 | ja | 99 | 90 | 89 | 12 | 3 | 80 | 1 | +0.24 | 371 / 88 / 400 |
| deepseek-v4.1-flash | en | 100 | 100 | 100 | 2 | 91 | 7 | 0 | +0.18 | 242 / 153 / 641 |
| deepseek-v4.1-flash | ko | 100 | 6 | 6 | 38 | 60 | 0 | 0 | +0.00 | 0 / 0 / 6 |
| deepseek-v4.1-flash | zh | 100 | 100 | 100 | 9 | 50 | 20 | 21 | +0.35 | 792 / 137 / 187 |
| deepseek-v4.1-flash | ja | 100 | 61 | 61 | 64 | 17 | 1 | 18 | +0.20 | 36 / 12 / 165 |
| qwen3.8-flash | en | 100 | 100 | 99 | 2 | 40 | 55 | 3 | -0.02 | 276 / 579 / 407 |
| qwen3.8-flash | ko | 100 | 100 | 98 | 15 | 33 | 52 | 0 | +0.40 | 566 / 47 / 233 |
| qwen3.8-flash | zh | 100 | 100 | 100 | 0 | 5 | 95 | 0 | +0.54 | 1250 / 55 / 37 |
| qwen3.8-flash | ja | 100 | 100 | 100 | 45 | 17 | 20 | 18 | +0.21 | 325 / 187 / 330 |
| solar-mini4 | en | 100 | 99 | 90 | 22 | 75 | 3 | 0 | +0.05 | 39 / 32 / 408 |
| solar-mini4 | ko | 100 | 98 | 88 | 46 | 37 | 15 | 1 | +0.43 | 211 / 12 / 210 |
| solar-mini4 | zh | 100 | 100 | 100 | 4 | 4 | 92 | 0 | +0.64 | 1213 / 25 / 128 |
| solar-mini4 | ja | 100 | 100 | 96 | 23 | 31 | 34 | 11 | +0.39 | 237 / 34 / 457 |

## Top descriptors per cell (share of dragon-sense responses)

### en `Dragon is`

- **gpt-6-luna** (n=93): mythical creature 63%, fire 18%, mythology 15%, folklore 14%, wings 14%, reptilian 13%, power 12%, large 12%, zodiac 10%, claws 9%
- **claude-haiku-4.5** (n=100): fire 87%, power 85%, wisdom 79%, wings 76%, mythical creature 71%, reptilian 62%, intelligence 58%, luck 53%, dangerous 44%, scales 41%
- **gemini-3.5-flash-lite** (n=100): fire 79%, mythical creature 78%, serpentine 63%, wings 59%, reptilian 50%, large 47%, monster 46%, luck 44%, wisdom 43%, water 36%
- **llama-4-maverick** (n=100): mythical creature 92%, power 88%, fire 86%, reptilian 77%, luck 74%, wings 63%, benevolent 56%, evil 52%, large 44%, wisdom 33%
- **mistral-small-2603** (n=87): mythical creature 56%, fire 43%, power 40%, wings 36%, reptilian 32%, wisdom 31%, serpentine 30%, magic 23%, mythology 21%, large 21%
- **deepseek-v4.1-flash** (n=100): wings 92%, mythical creature 88%, fire 82%, reptilian 78%, power 70%, wisdom 53%, serpentine 47%, luck 46%, scales 38%, benevolent 36%
- **qwen3.8-flash** (n=99): fire 81%, wings 69%, reptilian 65%, mythical creature 63%, power 62%, serpentine 57%, large 47%, evil 43%, greed 41%, scales 41%
- **solar-mini4** (n=90): mythical creature 59%, wings 48%, fire 40%, reptilian 34%, serpentine 32%, creature 31%, power 24%, claws 23%, large 20%, folklore 16%

### ko `용은`

- **gpt-6-luna** (n=80): mythical creature 상상 속의 동물 49%, creature 동물 18%, luck 행운 15%, scales 비늘 11%, flight 날다 11%, power 권력 11%, control 다스리다 11%, horns 뿔 10%, wisdom 지혜 10%, royalty 왕권 10%
- **claude-haiku-4.5** (n=100): power 권력 74%, luck 행운 54%, sacred 신성하다 49%, royalty 왕권 45%, mythical creature 상상 속의 동물 40%, prosperity 번영 36%, symbol 상징 36%, wisdom 지혜 30%, horns 뿔 28%, water 물 28%
- **gemini-3.5-flash-lite** (n=100): mythical creature 상상 속의 동물 84%, royalty 왕권 84%, guardian 수호신 64%, monster 괴물 56%, luck 행운 54%, destructive 파괴 49%, power 권력 40%, sacred 신성하다 37%, evil 악 33%, fire 뿜다 33%
- **llama-4-maverick** (n=77): serpentine 뱀 68%, mythical creature 상상 속의 동물 65%, power 권력 51%, luck 행운 49%, wings 날개 48%, evil 악 39%, benevolent 선하다 36%, legs 발 31%, creature 동물 26%, royalty 왕권 26%
- **mistral-small-2603** (n=93): royalty 왕권 56%, power 권력 52%, mythical creature 상상 속의 동물 42%, sacred 신성하다 31%, divine 신 28%, symbol 상징 27%, prosperity 번영 26%, authority 권위 23%, rain 비 22%, mysterious 신비롭다 18%
- **deepseek-v4.1-flash** (n=6): mythical creature 상상 속의 동물 100%
- **qwen3.8-flash** (n=98): royalty 왕권 46%, luck 행운 43%, mythical creature 상상 속의 동물 43%, sacred 신성하다 39%, power 권력 36%, wisdom 지혜 31%, rain 비 31%, serpentine 뱀 28%, horns 뿔 28%, flight 날다 28%
- **solar-mini4** (n=88): mythical creature 상상 속의 동물 53%, power 권력 33%, royalty 왕권 28%, flight 날다 25%, water 물 20%, rain 비 17%, symbol 상징 17%, sacred 신성하다 16%, luck 행운 16%, wisdom 지혜 15%

### zh `龙是`

- **gpt-6-luna** (n=95): power 力量 48%, luck 吉祥 47%, royalty 尊贵 45%, divine 神兽 38%, mythical creature 神异动物 36%, symbol 象征 20%, zodiac 十二生肖 11%, mythology 神话 5%, culture 龙的传人 4%, clouds 腾云驾雾 4%
- **claude-haiku-4.5** (n=100): luck 吉祥 98%, power 力量 97%, royalty 尊贵 83%, symbol 象征 49%, sacred 神圣 45%, mythical creature 神异动物 39%, wisdom 智慧 38%, rain 雨水 32%, horns 鹿角 30%, water 水 29%
- **gemini-3.5-flash-lite** (n=100): symbol 象征 99%, mythical creature 神异动物 96%, scales 鱼鳞 89%, claws 鹰爪 84%, horns 鹿角 84%, head 头似驼 82%, eyes 眼似兔 79%, paws 掌似虎 79%, ears 耳似牛 75%, abdomen 腹似蜃 58%
- **llama-4-maverick** (n=100): power 力量 82%, large 巨大 80%, reptilian 爬行动物 76%, scales 鱼鳞 60%, mythical creature 神异动物 56%, luck 吉祥 55%, serpentine 蛇身 50%, fire 喷火 46%, benevolent 仁慈 39%, fire breath 喷火 37%
- **mistral-small-2603** (n=99): power 力量 76%, luck 吉祥 71%, royalty 尊贵 60%, scales 鱼鳞 49%, mythical creature 神异动物 48%, horns 鹿角 47%, symbol 象征 46%, claws 鹰爪 43%, serpentine 蛇身 40%, wisdom 智慧 30%
- **deepseek-v4.1-flash** (n=100): symbol 象征 84%, luck 吉祥 80%, royalty 尊贵 75%, power 力量 72%, mythical creature 神异动物 54%, divine 神兽 44%, authority 权威 42%, creature 生物 37%, monster 巨兽 29%, rain 雨水 26%
- **qwen3.8-flash** (n=100): luck 吉祥 97%, power 力量 95%, royalty 尊贵 87%, authority 权威 79%, symbol 象征 54%, rain 雨水 46%, horns 鹿角 39%, divine 神兽 37%, scales 鱼鳞 37%, clouds 腾云驾雾 37%
- **solar-mini4** (n=100): power 力量 100%, luck 吉祥 99%, royalty 尊贵 86%, rain 雨水 60%, divine 神兽 56%, majesty 威严 47%, water 水 45%, prosperity 繁荣 35%, authority 权威 34%, mythical creature 神异动物 33%

### ja `竜は`

- **gpt-6-luna** (n=74): mythical creature 伝説の生き物 58%, fire 火を吐く 50%, creature 生き物 35%, flight 空を飛ぶ 35%, wings 翼 20%, water 水 18%, sacred 神聖な存在 15%, rain 雨 14%, monster 怪物 14%, guardian 守る 9%
- **claude-haiku-4.5** (n=100): mythical creature 伝説の生き物 92%, power 力 80%, royalty 皇帝の象徴 60%, luck 幸運 58%, sacred 神聖な存在 56%, water 水 48%, wisdom 知恵 36%, water deity 水神 28%, flight 空を飛ぶ 25%, symbol 象徴 23%
- **gemini-3.5-flash-lite** (n=100): mythical creature 伝説の生き物 94%, royalty 皇帝の象徴 72%, serpentine 蛇 70%, horns 角 66%, reptilian 巨大なトカゲ 66%, wings 翼 64%, water deity 水神 56%, luck 幸運 50%, sacred 神聖な存在 45%, fire breath 火を吐く 43%
- **llama-4-maverick** (n=100): reptilian 巨大なトカゲ 66%, mythical creature 伝説の生き物 63%, power 力 58%, wings 翼 56%, luck 幸運 55%, fire breath 火を吐く 51%, creature 生き物 36%, villain 悪役 35%, mysterious 神秘性 28%, sacred 神聖な存在 24%
- **mistral-small-2603** (n=89): mythical creature 伝説の生き物 80%, scales 鱗 51%, horns 角 48%, power 力 42%, royalty 皇帝の象徴 40%, serpentine 蛇 36%, sacred 神聖な存在 35%, claws 爪 29%, wings 翼 26%, legs 四本の足 25%
- **deepseek-v4.1-flash** (n=61): mythical creature 伝説の生き物 92%, flight 空を飛ぶ 87%, power 力 31%, water 水 18%, western dragon 西洋のドラゴン 10%, eastern dragon 東洋の竜 10%, rain 雨 10%, royalty 皇帝の象徴 10%, luck 幸運 7%, fire 火を吐く 5%
- **qwen3.8-flash** (n=100): mythical creature 伝説の生き物 36%, flight 空を飛ぶ 34%, guardian 守る 31%, rain 雨 31%, sacred 神聖な存在 30%, fire 火を吐く 29%, water 水 26%, power 力 25%, serpentine 蛇 22%, royalty 皇帝の象徴 21%
- **solar-mini4** (n=96): mythical creature 伝説の生き物 73%, flight 空を飛ぶ 46%, power 力 40%, royalty 皇帝の象徴 34%, water 水 30%, authority 権威 29%, rain 雨 27%, sacred 神聖な存在 23%, divine 霊獣 22%, wings 翼 22%
