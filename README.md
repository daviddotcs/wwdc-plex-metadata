# WWDC Plex Metadata Agent
A Plex agent which provides metadata for [Apple Worldwide Developers Conference](https://developer.apple.com/wwdc/) session videos including titles, dates, summaries, and collection tags.

## Requirements
* An installation of [Plex Media Server](https://www.plex.tv/).

## Installation
1. Download or clone this repository and copy **WWDC.bundle** into your [Plex Plug-ins directory](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-). E.g.;  

 | Platform | Directory |
 | -------- | --------- |
 | Linux    | /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins/ |
 | macOS    | ~/Library/Application Support/Plex Media Server/Plug-ins/ |
 | Windows  | %LOCALAPPDATA%\Plex Media Server\Plug-ins\ |

2. In your Plex web interface visit **Settings > Server > Agents** and verify that you have a *WWDC* agent listed under *Movies*.
3. Edit or create a new Movies or Home Vidoes library for a directory with WWDC session videos, and from the *Advanced* tab select the *WWDC* agent.

## File and Folder Structure
This agent requires file names to include the 3 digit session number as the first number in the filename, and for the parent directory to be named including a 2 or 4 digit year number e.g.;
```
/WWDC 2016/805_hd_iterative_ui_design.mp4
```
The above example will be correctly parsed as session number 805 from WWDC 2016.

## Limitations
* Session thumbnails are not currently fetched.
* Name matches are not implemented, so year and session numbers are crucial.

