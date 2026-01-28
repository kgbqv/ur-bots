# Royal Game of Ur – Bot Playground

## Run a match
```

python play.py

```

## Train Q-learning bot
```

python training/qlearn.py

```

This saves `qbot.pkl`.

## Use trained bot
```python
from bots.qbot import QBot
bot = QBot("qbot.pkl")
```

