# Rainbow Brackets

![logo](icon.png)

This extension allows matching brackets to be identified with colours. The user can define which characters to match, and which colors to use.

![Version](https://vsmarketplacebadge.apphb.com/version-short/tal7aouy.rainbow-bracket.svg?style=for-the-badge&colorA=252526&colorB=43A047&label=VERSION)
![Rating](https://vsmarketplacebadge.apphb.com/rating-short/tal7aouy.rainbow-bracket.svg?style=for-the-badge&colorA=252526&colorB=43A047&label=Rating)
![Installs](https://vsmarketplacebadge.apphb.com/installs-short/tal7aouy.rainbow-bracket.svg?style=for-the-badge&colorA=252526&colorB=43A047&label=Installs)
![Downloads](https://vsmarketplacebadge.apphb.com/downloads-short/tal7aouy.rainbow-bracket.svg?style=for-the-badge&colorA=252526&colorB=43A047&label=Downloads)

## Table of Contents

- [Supported languages](#supported-languages)
- [Author's choice](#authors-choice)
- [Install](#install)
- [Screenshots](#screenshots)
- [Settings](#settings)
- [Commands](#commands)
- [HTML Configuration](#html-configuration)
- [Release Notes](#changelog)
- [Issues & Suggestions](#issues--suggestions)

## Supported languages

Java, Scala, Clojure, Kotlin, Python, Haskell, Agda, Rust, JavaScript, TypeScript, Erlang, Go, Groovy, Ruby, Elixir, ObjectiveC, PHP, HTML, XML, SQL, Apex language, C#, Dart, Pug/Jade, Bash, Vue.js, C# Razor Pages, GLSL(the OpenGL Shading Language), Go Template, C++, C...

## Author's choice

Rainbow Brackets + Theme + Error Lens +[Monolisa](https://www.monolisa.dev/) (Font)

## install

1. Open the extensions sidebar on Visual Studio Code
1. Search for **Rainbow Brackets**
1. Click Install
1. Click Reload to reload your editor
1. 🌟🌟🌟🌟🌟 Rate five-stars 😃

## Screenshots

- Python

![Python code example with Rainbow Brackets](./images/python.png)
![Rainbow Brackets code example](./images/rainbow.png)

- Typescript

![TypeScript code example with Rainbow Brackets](./images/typescript.png)

- Vue

![Vue code example with Rainbow Brackets](./images/vue.png)

## Settings

```json
// default is 200
"RainbowBrackets.timeOut":200
```

Configure how long the editor should be idle for before updating the document.

> Set to 0 to disable.

```json
"RainbowBrackets.forceUniqueOpeningColor": true | false
```

> ![Disabled](images/forceUniqueOpeningColorDisabled.png "forceUniqueOpeningColor Disabled") > ![Enabled](images/forceUniqueOpeningColorEnabled.png "forceUniqueOpeningColor Enabled")

```json
"RainbowBrackets.forceIterationColorCycle": true
```

> ![Enabled](images/forceIterationColorCycleEnabled.png "forceIterationColorCycle Enabled")

### Commands

These commands will expand/undo the cursor selection to the next scope

`"rainbow-brackets.expandBracketSelection"`  
`"rainbow-brackets.undoBracketSelection"`

Quick-start:

```json
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

### HTML Configuration

> An example configuration for HTML is:

```json
    "RainbowBrackets.consecutivePairColors": [
    "()",
    "[]",
    "{}",
    ["teal", "yellow", "tomato"],
    "Revioletd"
  ]
```

`settings.json`

```json
{
  "editor.RainbowBrackets.enabled": true,
  "editor.guides.bracketPairs": "active"
}
```

Screenshot:  
![Screenshot](images/example.png "Rainbow Brackets")

---

## Features

### User defined matching characters

By default (), [], and {} are matched, however custom bracket characters can also be configured.

---

## [CHANGELOG](CHANGELOG.md)

---

## Issues & Suggestions

For any issues or suggestions, please use [GitHub issues](https://github.com/tal7aouy/RainbowBrackets/issues).
