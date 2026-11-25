# ידיעת הארץ: החידון של המילואים

A Hebrew trivia quiz for reservists: 310 multiple-choice questions on history, geography, Tanakh, presidents and prime ministers, Zionism, and world knowledge, with some funny ones along the way.

It is a single-page web app. It works offline and can be installed on a phone like an app.

## What's in this repository

| Path | What it is |
|---|---|
| `index.html` | The whole app: questions, fonts and map background are all inside this one file. |
| `manifest.json`, `sw.js`, `icon-*.png` | What lets phones install the app and use it offline. |
| `source/questions/` | The questions, one file per topic (plus `humor.json`). Edit these to change questions. |
| `source/app/` | The design template, fonts, map background and the build script. |
| `source/SPEC.md` | The rules the questions were written by (format, tone, accuracy). |

## Publishing (GitHub Pages)

Settings → Pages → Branch: `main`, folder `/ (root)` → Save.
The app is then live at `https://shakedgozlan.github.io/yediat-haaretz/`.

## Changing or adding questions

1. Edit a file in `source/questions/`. Each question looks like this:

   ```json
   {
     "id": "geo-046",
     "cat": "geography",
     "q": "The question",
     "options": ["answer 1", "answer 2", "answer 3", "answer 4"],
     "answer": 0,
     "explain": "One or two sentences shown after answering.",
     "difficulty": 2,
     "funny": false,
     "joke": false,
     "source": "https://link-that-proves-the-answer"
   }
   ```

   `answer` is the position of the correct option, counting from 0. `difficulty` is 1 (easy), 2 (medium) or 3 (hard). `joke: true` marks a riddle-joke that is not counted in the score.

2. Rebuild the app from the repository root:

   ```
   python3 source/app/build.py
   ```

   The script checks every question (four different options, a valid answer, a source) and stops with a list of problems if something is wrong. It needs Python with the Pillow package.

3. In `sw.js` (both the root copy and `source/app/sw.js`), raise the version number, for example `v2` to `v3`, so phones download the new questions.

4. Commit and push.

## Credits

- Fonts: Rubik Dirt and Secular One, both under the SIL Open Font License (licenses in `source/app/fonts-v2/`).
- Questions were researched and fact-checked against public sources; each question links to its source.
