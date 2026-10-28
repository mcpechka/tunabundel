# tunabundel

De muziek bundel van Tuna Ciudad de Luz. 

Cancionero de Tuna Ciudad de Luz. 

Music bundle of Tuna Ciudad de Luz made in LaTeX.


## Software requirements
 
- [LaTeX](https://www.latex-project.org/)
- [LilyPond](https://lilypond.org/)

## Cancionero Común (website)

`index.html` is a website that builds a shared songbook from the files in this repo: every song in `bundel/Tunabundel2.tex`, with transposing, DO-RE-MI / C-D-E notation and side-by-side chord comparison between tunas.

Other tunas can join by adding a folder under `tunas/` (a `tuna.json` plus songs in ChordPro `.cho` or Tunabundel `.tex`) and listing it in `tunas/index.json`. The site's "Añade tu tuna" tab explains the format.

Published with GitHub Pages from the `master` branch (root folder).
