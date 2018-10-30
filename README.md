# plumo_pytorch

nvidia-docker is needed to run the program.
```
Usage:

./run.sh  input output

input: an input directory containing dicom files (input/*.dcm).
output: output directory where results (HTML) are written to.
```
If multiple GPUs are supplied, parameter  ```'n_gpu'``` in ```res/patch``` may be modified accordingly. Changing other parameters in that file is not advised, though.

Output folder will contain sub-directories for each input sample. A HTML file will be available inside for viewing predictions. Since DICOM files are used for viewing, remotely opening the web page may be a slow process. 
