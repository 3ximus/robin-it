# Change Log

## [v1.0](https://github.com/3ximus/robin-it/tree/v1.0) (2016-11-06)
[Full Changelog](https://github.com/3ximus/robin-it/compare/v0.5...v1.0)

- Basic tracking system fullt implemented
    - See shows left to watch
- GUI stability and coherence improvements
- Settings menu functionality


**Fixed bugs:**

- Total number of shows that is used for the widget progress bar does not account for airdate [\#54](https://github.com/3ximus/robin-it/issues/54)
- Fied background redraws for scoll areas [\#50](https://github.com/3ximus/robin-it/issues/50)
- Marking a show not tracked \(forcing tracking\) does not save watched status [\#35](https://github.com/3ximus/robin-it/issues/35)
- Lock buttons while loading show on ShowWindow, otherwise clicking on them crashes the program [\#32](https://github.com/3ximus/robin-it/issues/32)
- Force windows to wait for all threads before exiting?? [\#29](https://github.com/3ximus/robin-it/issues/29)
- If there is a search ongoing, starting a new search displays the results being added to the previous one [\#25](https://github.com/3ximus/robin-it/issues/25)
- Resizing window pixelates the background [\#20](https://github.com/3ximus/robin-it/issues/20)

**Closed issues:**

- Convert to watch button to a checkbox [\#55](https://github.com/3ximus/robin-it/issues/55)
- Show some kind of progress bar on show widgets to display completion status [\#53](https://github.com/3ximus/robin-it/issues/53)
- Add a label to show window to display when this show was last updated [\#52](https://github.com/3ximus/robin-it/issues/52)
- Make episode description appear when hovered instead of clicked [\#51](https://github.com/3ximus/robin-it/issues/51)
- Cache image downloads [\#48](https://github.com/3ximus/robin-it/issues/48)
- Download function wrapper to make cache possible [\#47](https://github.com/3ximus/robin-it/issues/47)
- Display all episodes left to watch [\#45](https://github.com/3ximus/robin-it/issues/45)
- Fix high memory consumption [\#44](https://github.com/3ximus/robin-it/issues/44)
- Auto update tracked show info [\#38](https://github.com/3ximus/robin-it/issues/38)
- Add option to see episode info \(maybe as a popup widget\) [\#37](https://github.com/3ximus/robin-it/issues/37)
- Add statusbar when adding/marking shows because it may take some time [\#33](https://github.com/3ximus/robin-it/issues/33)
- Use a config class to handle all config file interactions and make it easier to add new config options [\#31](https://github.com/3ximus/robin-it/issues/31)
- Clean ShowMenu.display\_results [\#30](https://github.com/3ximus/robin-it/issues/30)
- Make settigns available globally [\#21](https://github.com/3ximus/robin-it/issues/21)
- Add option to see followed tv shows info [\#16](https://github.com/3ximus/robin-it/issues/16)
- Add option to see queued episodes in detail [\#15](https://github.com/3ximus/robin-it/issues/15)
- Able to select episode range and episode count [\#3](https://github.com/3ximus/robin-it/issues/3)
- Get an API Key from the tvdb [\#1](https://github.com/3ximus/robin-it/issues/1)

## [v0.5](https://github.com/3ximus/robin-it/tree/v0.5) (2016-10-04)
[Full Changelog](https://github.com/3ximus/robin-it/compare/v0.4...v0.5)

- Stability Improvements

**Fixed bugs:**

- When logging in for the first time it crashes when searching [\#24](https://github.com/3ximus/robin-it/issues/24)
- Fix erros when image url not available in episode [\#22](https://github.com/3ximus/robin-it/issues/22)

**Closed issues:**

- Add a way to remove a show when searching for it [\#23](https://github.com/3ximus/robin-it/issues/23)

## [v0.4](https://github.com/3ximus/robin-it/tree/v0.4) (2016-10-04)
[Full Changelog](https://github.com/3ximus/robin-it/compare/v0.3...v0.4)

- Delete followed shows
- Mark shows, seasons or episodes as watched

## [v0.3](https://github.com/3ximus/robin-it/tree/v0.3) (2016-10-03)
[Full Changelog](https://github.com/3ximus/robin-it/compare/v0.2...v0.3)

- Able to add shows

**Fixed bugs:**

- Shows without image dont show on the search [\#19](https://github.com/3ximus/robin-it/issues/19)
- Dont allow to add show when it is already being followed [\#12](https://github.com/3ximus/robin-it/issues/12)

## [v0.2](https://github.com/3ximus/robin-it/tree/v0.2) (2016-10-01)
[Full Changelog](https://github.com/3ximus/robin-it/compare/v0.1...v0.2)

- TVShow search function

## [v0.1](https://github.com/3ximus/robin-it/tree/v0.1) (2016-09-26)

- Preliminar GUI version

**Fixed bugs:**

- TV shows with strange names cant be searched correctly [\#14](https://github.com/3ximus/robin-it/issues/14)
- Dont crash when internet connection isnt available [\#13](https://github.com/3ximus/robin-it/issues/13)

**Closed issues:**

- Fix requirements.txt for colorama [\#11](https://github.com/3ximus/robin-it/issues/11)
- Make list of output when gathering or downloading instead of just one line [\#10](https://github.com/3ximus/robin-it/issues/10)
- Fix : Cannot select torrent from results [\#8](https://github.com/3ximus/robin-it/issues/8)
- Make episode list an attribute of UserContent so that it can be persistent and queued etc.. [\#7](https://github.com/3ximus/robin-it/issues/7)
- Add way to abort episode selection process [\#5](https://github.com/3ximus/robin-it/issues/5)



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*