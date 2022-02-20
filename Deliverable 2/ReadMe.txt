This Part is for the second deliverable.
The Meta Data and the "Downloads" folder is for the HPC Code "Text Anaylsis Parameter Detection"
In this python file, one can see the code for the optimal parameters for the different text analysis methods.
Additionally, the time used for the methods is also shown. The excel file is the manual accuracy check of the final method of text analysis with the optimized parameters.


In the "HPC Code" folder one can see the code for using the text analysis on a high performance computer.
Of course, one can also use the "Text Analysis Parameter Detection" file for text analysis if wanted.
To run the HPC code, one has to upload the content of the folder to an HPC, as well as the shortened treaty texts folders from deliverable 1.
Then running the command "sbatch --array=n-m array_thread_HPC_whole_folder.sh folder_name"
where n to m are the beginning and end number of the batches folder one wishes to run and folder_name is the folder name one wishes to run for Ecolex treaty decision names.
Similarly, the command sbatch --array=n-m stata_array_HPC_threading.sh folder_name" will run the text analysis for IEA treaty names.
(This was tested on the Snellius HPC, for other HPCs this command might deviate)