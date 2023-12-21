import os
import re
import random
from flask import Flask, request, jsonify, Response
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)

class VideoProcessor:
    def __init__(self):
        self.video_files = []
        self.random_sample_folder = ''

    def process_and_sample(self, data):
        if 'input_paths' not in data or 'clip_length' not in data or 'fps' not in data or 'output_path' not in data:
            return Response("Please provide input_paths, clip_length, fps, and output_path in the request data.", status=400)

        try:
            clip_length = float(data['clip_length'])
            fps = int(data['fps'])
            sample_percentage = float(data.get('sample_percentage'))
        except ValueError:
            return Response("Invalid value for clip_length, fps, or sample_percentage.", status=400)

        if clip_length <= 0 or fps <= 0 or sample_percentage <= 0 or sample_percentage > 100:
            return Response("Invalid values for clip_length, fps, or sample_percentage.", status=400)

        input_paths = [path.strip() for path in data['input_paths'].split(',')]

        clips_info_dict = {}
        video_counter = 0
        for input_path in input_paths:
            video_info = self.process_single_video_for_info(video_counter,input_path, clip_length, fps)
            video_counter += 1
            clips_info_dict[input_path] = video_info

        sampled_clips_info = self.sample_clips(clips_info_dict, sample_percentage)

        output_path = data['output_path']
        result = self.create_clips(sampled_clips_info, output_path)

        file_list = self.list_files(self.random_sample_folder)
        clip_number_counter = 0  # Initialize the clip number counter

        for file_name in file_list:
            original_path = os.path.join(self.random_sample_folder, file_name)

            # Extract parts directly without using re.search
            try:
                video_number, start_time_str, end_time_str, fps_str = self.extract_parts(file_name)

                # Construct the new clip number
                clip_number = clip_number_counter
                clip_number_counter += 1

                new_name = f"video_{video_number}_clip_{clip_number}_{start_time_str}_to_{end_time_str}_{fps_str}fps.mp4"
                new_path = os.path.join(self.random_sample_folder, new_name)

                print(f"Renaming: {original_path} -> {new_path}")
                os.rename(original_path, new_path)
                print(f"Renamed: {original_path} -> {new_path}")
            except IndexError:
                print(f"Skipping file: {original_path} (does not match the expected pattern)")

        return jsonify(result)
    
    def list_files(self, directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        sorted_files = sorted(files, key=lambda x: [int(c) if c.isdigit() else c for c in re.split('(\d+)', x)])
        return sorted_files

    def extract_parts(self, file_name):
        parts = file_name.split('_')
        video_number = int(parts[1])  # Extract video number
        start_time_str = parts[4] + "_" + parts[5]  # Adjust index for start time
        end_time_str = parts[7] + "_" + parts[8]  # Adjust index for end time
        fps_str = parts[9].split('fps')[0]
        return video_number, start_time_str, end_time_str, fps_str

    def process_single_video_for_info(self, video_counter, video_file, clip_length, fps):
        video_clip = VideoFileClip(video_file)
        video_duration = video_clip.duration

        num_clips = int(video_duration / clip_length)

        clips_info = []
        for i in range(num_clips):
            start_time = i * clip_length
            end_time = start_time + clip_length

            clip_info = {
                "clip_number": i,
                "start_time": start_time,
                "end_time": end_time,
                "fps": fps,
                "video_number": video_counter  # Assuming there is only one video in this example
            }

            clips_info.append(clip_info)

        return clips_info

    def sample_clips(self, clips_info_dict, sample_percentage):
        sampled_clips_info = {}
        for video_path, clips_info in clips_info_dict.items():
            total_clips = len(clips_info)
            sample_size = int((sample_percentage / 100.0) * total_clips)

            if sample_size > 0:
                sampled_clips = random.sample(clips_info, sample_size)
                sampled_clips_info[video_path] = sampled_clips

        return sampled_clips_info

    def create_clips(self, sampled_clips_info, output_path):
        for video_path, clips_info in sampled_clips_info.items():
            video_clip = VideoFileClip(video_path)
            video_number = clips_info[0]['video_number']

            # Create a random folder name to avoid collisions
            folder_name = "random_sample"
            output_folder = os.path.join(output_path, folder_name)

            self.random_sample_folder = output_folder

            os.makedirs(output_folder, exist_ok=True)

            for clip_info in clips_info:
                start_time = clip_info['start_time']
                end_time = clip_info['end_time']
                clip_number = clip_info['clip_number']
                fps = clip_info['fps']

                # Convert start time and end time to the desired format
                start_time_formatted = "{:02d}_{:02d}".format(int(start_time) // 60, int(start_time) % 60)
                end_time_formatted = "{:02d}_{:02d}".format(int(end_time) // 60, int(end_time) % 60)

                clip = video_clip.subclip(start_time, end_time)
                output_name = f"video_{video_number}_clip_{clip_number}_{start_time_formatted}_to_{end_time_formatted}_{fps}fps.mp4"
                clip_output_path = os.path.join(output_folder, output_name)
                
                # Ensure the parent folder exists before writing the file
                os.makedirs(os.path.dirname(clip_output_path), exist_ok=True)
                
                clip.write_videofile(clip_output_path, fps=fps)

            video_clip.close()

        return {"message": "Random sample created successfully."}



processor = VideoProcessor()

@app.route('/process_and_sample', methods=['POST'])
def process_and_sample():
    data = request.form if request.form else request.json
    result = processor.process_and_sample(data)
    return result

if __name__ == '__main__':
    app.run(debug=True)
