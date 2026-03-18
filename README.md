# 🌈 Rainbow Brackets


## Supported Languages

Java, Scala, Clojure, Kotlin, Python, Haskell, Agda, Rust, JavaScript, TypeScript, Erlang, Go, Groovy, Ruby, Elixir, Objective-C, PHP, HTML, XML, SQL, Apex, C#, Dart, Pug/Jade, Bash, Vue.js, C# Razor Pages, GLSL (OpenGL Shading Language), Go Template, C++, C…


## Installation

1. Open the **Extensions** sidebar in Visual Studio Code.
2. Search for `Rainbow Brackets`.
3. Click **Install**.
4. Click **Reload** to reload your editor.

🌟🌟🌟🌟🌟 **Rate five stars 😃**


## Settings

```json id="rainbow-settings"
"RainbowBrackets.timeOut": 200, // default is 200ms, set 0 to disable
"RainbowBrackets.forceUniqueOpeningColor": true, // or false
"RainbowBrackets.forceIterationColorCycle": true
```

---

## Commands

Expand or undo cursor selection to the next bracket scope:

```json id="rainbow-commands"
{
  "key": "shift+alt+right",
  "command": "rainbow-brackets.expandBracketSelection",
  "when": "editorTextFocus"
},
{
  "key": "shift+alt+left",
  "command": "rainbow-brackets.undoBracketSelection",
  "when": "editorTextFocus"
}
```

---

## HTML Configuration Example

```json id="rainbow-html"
"RainbowBrackets.consecutivePairColors": [
  "()",
  "[]",
  "{}",
  ["teal", "yellow", "tomato"],
  "Revioletd"
]
```

`settings.json` snippet:

```json id="rainbow-json"
{
  "editor.RainbowBrackets.enabled": true,
  "editor.guides.bracketPairs": "active"
}
```

---

## Features

* User-defined matching characters
* By default `()`, `[]`, and `{}` are matched
* Custom bracket characters can also be configured


## Issues & Suggestions

For any issues or suggestions, please use **[GitHub Issues](link-to-github)**

