<h1>Video Sampling System</h1>

<p>This project implements a video sampling system using Flask as an API to process and sample video clips. The system offers two distinct methods for video sampling: Traditional Sampling and Dynamic Sampling.</p>

<h2>Table of Contents</h2>

<ul>
  <li><a href="#overview">Overview</a></li>
  <li><a href="#methods">Methods</a></li>
    <ul>
      <li><a href="#traditional-sampling">Traditional Sampling</a></li>
      <li><a href="#dynamic-sampling">Dynamic Sampling</a></li>
    </ul>
  <li><a href="#modules-used">Modules Used</a></li>
  <li><a href="#how-to-use">How to Use</a></li>
    <ul>
      <li><a href="#api-endpoint">API Endpoint</a></li>
      <li><a href="#input-parameters">Input Parameters</a></li>
    </ul>
</ul>

<h2>Overview</h2>

<p>The video sampling system provides an automated and efficient way to generate diverse samples from input videos. The implementation includes two methods, Traditional Sampling and Dynamic Sampling, each offering unique advantages based on user requirements.</p>

<h2>Methods</h2>

<h3>Traditional Sampling</h3>

<p>Method 1 involves processing all video clips in the initial step and then randomly selecting clips based on the specified sample percentage. The clips are then placed into a randomly chosen folder, and a final renaming process ensures sequential numbering.</p>

<h3>Dynamic Sampling</h3>

<p>Method 2 adopts a dynamic sampling approach, collecting information about individual video clips first. Random sampling is then directly applied to this collected information, enhancing efficiency, especially with large video datasets. This method allows for targeted and flexible selection.</p>

<h2>Modules Used</h2>

<ul>
  <li><strong>Operating System (os) Library:</strong>
    <ul>
      <li><code>os.path.exists:</code> Checks if a specified path exists.</li>
      <li><code>os.path.join:</code> Joins paths for folder creation and file handling.</li>
      <li><code>os.makedirs:</code> Creates folders for storing processed video clips.</li>
      <li><code>os.listdir:</code> Lists files in a directory for various operations.</li>
      <li><code>os.rename:</code> Renames video clips during the final renaming step.</li>
    </ul>
  </li>
  <li><strong>File Operations (shutil) Library:</strong>
    <ul>
      <li><code>shutil.copy:</code> Copies sampled video clips to a designated folder.</li>
      <li><code>shutil.move:</code> Moves sampled video clips to their final destination during the renaming process.</li>
    </ul>
  </li>
  <li><strong>Regular Expressions (re) Library:</strong>
    <ul>
      <li><code>re.split:</code> Applied in parsing clip names to extract relevant details, aiding in the systematic organization and naming of sampled video clips.</li>
    </ul>
  </li>
  <li><strong>Flask Library:</strong>
    <ul>
      <li><code>Flask.request:</code> Handles the incoming request data.</li>
      <li><code>Flask.jsonify:</code> Converts the result to a JSON response.</li>
    </ul>
  </li>
  <li><strong>random Library:</strong>
    <ul>
      <li><code>random.sample:</code> Randomly selects video clips based on a specified percentage.</li>
    </ul>
  </li>
  <li><strong>VideoFileClip Class (from moviepy Library):</strong>
    <ul>
      <li><code>VideoFileClip.subclip:</code> Extracts a subclip from the original video based on start and end times.</li>
      <li><code>VideoFileClip.write_videofile:</code> Writes the trimmed clip to a specified output path with specified codec and parameters.</li>
    </ul>
  </li>
</ul>

<h2>How to Use</h2>

<h3>API Endpoint</h3>

<p>The system provides a Flask-based API with the endpoint <code>/process_and_sample</code>. This endpoint receives POST requests from the frontend application to initiate the video processing workflow.</p>

<h3>Input Parameters</h3>

<p>To use the API, provide the following input parameters:</p>

<ul>
  <li><code>input_paths:</code> Comma-separated paths of input videos.</li>
  <li><code>output_path:</code> Path to the output directory.</li>
  <li><code>clip_length:</code> Duration of each sampled video clip.</li>
  <li><code>fps:</code> Frames per second for video processing.</li>
  <li><code>sample_percentage:</code> Percentage of clips to be sampled (optional for Method 2).</li>
</ul>

<p>For a successful request, ensure all critical parameters are included. Refer to the specific method details for additional considerations.</p>

