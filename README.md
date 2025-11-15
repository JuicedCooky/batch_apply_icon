# batch_apply_icon
apply icon to folders using exe

| argunent | value | explaination |
|---|---|---|
| --directory | path/str | the path to the folder to apply the icon or the parent folder containing other folders |
| --is-parent | bool | specifies if the directory is a parent containing other folders to add icons |
| --depth | int | number of subfolders, how many folders to navigate until the desired folders to add icons to |

if depth==0 apply icons to every folder within the parent directory folder
parent
  - folder to apply icon
  - folder to apply icon
  - folder to apply icon 
  - folder to apply icon


if depth==1 apply icons to every folder within each folder within the parent
parent
  - folder
    - folder to apply icon
    - folder to apply icon
    - folder to apply icon 
  - folder
    - folder to apply icon
    - folder to apply icon
