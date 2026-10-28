# tunabundel

De muziek bundel van Tuna Ciudad de Luz. 

Cancionero de Tuna Ciudad de Luz. 

Music bundle of Tuna Ciudad de Luz made in LaTeX.


## Software requirements
 
- [LaTeX](https://www.latex-project.org/)
- [LilyPond](https://lilypond.org/)

## Cancionero Común (website)

Full background, formats, known issues and roadmap: [documentation/CANCIONERO.md](documentation/CANCIONERO.md).

`index.html` is a website that builds a shared songbook from the files in this repo: every song in `bundel/Tunabundel2.tex`, with transposing, DO-RE-MI / C-D-E notation and side-by-side chord comparison between tunas.

Other tunas can join by adding a folder under `tunas/` (a `tuna.json` plus songs in ChordPro `.cho` or Tunabundel `.tex`) and listing it in `tunas/index.json`. The site's "Añade tu tuna" tab explains the format.

Published with GitHub Pages from the `master` branch (root folder).

### ChordPro

Every song in `bundel/songs/` also exists as ChordPro in `bundel/chordpro/` (same file name, `.cho`). The website reads these; the LaTeX bundel still builds from the `.tex` files. After editing a `.tex` song, regenerate the ChordPro files with:

```
python3 tools/tex2cho.py bundel/songs bundel/chordpro
```

Bandurria tab numbers become ChordPro annotations (`[*50 52]`), fingering hints become `{define}` lines, and the Dutch translations are kept as a `Vertaling (NL)` section.
