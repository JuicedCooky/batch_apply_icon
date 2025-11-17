# batch_apply_icon
apply icon to folders using exe

| argunent | value | explaination |
|---|---|---|
| --directory | path/str | the path to the folder to apply the icon or the parent folder containing other folders |
| --is-parent | bool | specifies if the directory is a parent containing other folders to add icons |
| --depth | int | number of subfolders, how many folders to navigate until the desired folders to add icons to |
| --exe | bool | whether to look for icons in .exe files |
| --ico | bool | whether to look for icons in .ico files |
| --image | bool | whether to look for icons in image files |

if depth==0 apply icons to every folder within the parent directory folder
<br/><br/>
parent<br/>
  &emsp;\- folder to apply icon<br/>
  &emsp;\- folder to apply icon<br/>
  &emsp;\- folder to apply icon <br/>
  &emsp;\- folder to apply icon<br/>


if depth==1 apply icons to every folder within each folder within the parent
<br/><br/>
parent<br/>
  &emsp;\- folder<br/>
    &emsp;&emsp;\- folder to apply icon<br/>
    &emsp;&emsp;\- folder to apply icon<br/>
    &emsp;&emsp;\- folder to apply icon <br/>
  &emsp;\- folder<br/>
    &emsp;&emsp;\- folder to apply icon<br/>
    &emsp;&emsp;\- folder to apply icon<br/>
