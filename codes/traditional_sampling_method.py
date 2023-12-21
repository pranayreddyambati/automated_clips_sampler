import os
import random
import shutil
import re
from flask import Flask, request, jsonify
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)

class VideoProcessor:
    def __init__(self):
        self.output_path = ""
        self.video_files = []

    def process_and_sample(self, data):
        if 'input_paths' not in data or 'output_path' not in data or 'clip_length' not in data or 'fps' not in data or 'sample_percentage' not in data:
            return {"error": "Please provide input_paths, output_path, clip_length, and fps in the request data."}, 400

        self.output_path = data['output_path']

        try:
            clip_length = float(data['clip_length'])
            fps = int(data['fps'])
            sample_percentage = float(data['sample_percentage'])
        except ValueError:
            return {"error": "Invalid value for clip_length or fps."}, 400

        if not self.output_path or not clip_length or not fps:
            return {"error": "Please fill in all the required fields."}, 400

        input_paths = [path.strip() for path in data['input_paths'].split(',')]

        for video_number, input_path in enumerate(input_paths):
            if os.path.exists(input_path):
                self.video_files.append({"video_number": video_number, "path": input_path})
            else:
                return {"error": f"File not found: {input_path}"}, 400

        # Video processing
        for video_info in self.video_files:
            video_file = video_info["path"]
            video_number = video_info["video_number"]
            self.process_single_video(video_file, clip_length, fps, video_number)

        all_clips_folder = os.path.join(self.output_path, 'all_clips')

        # Random sampling
        video_clips = self.get_video_clips(all_clips_folder)

        random_sample_folder = os.path.join(self.output_path, 'random_sample')
        os.makedirs(random_sample_folder, exist_ok=True)

        for video_number, clips in video_clips.items():
            total_clips = len(clips)
            sample_size = int(total_clips * sample_percentage / 100)

            if sample_size > total_clips:
                print(f"Error: Sample size ({sample_size}) is greater than the total number of clips ({total_clips}).")
                return

            selected_clips = random.sample(clips, sample_size)

            for clip_name in selected_clips:
                clip_path = os.path.join(all_clips_folder, clip_name)
                output_path = os.path.join(random_sample_folder, clip_name)

                print(f"Copying: {clip_path} -> {output_path}")

                # Copy the selected clip to the random sample folder
                shutil.copy(clip_path, output_path)
                print(f"Copied: {clip_path} -> {output_path}")

        print(f"All random samples created in: {random_sample_folder}")

        # Renaming

        file_list = self.list_files(random_sample_folder)
        clip_number_counter = 0  # Initialize the clip number counter

        for file_name in file_list:
            original_path = os.path.join(random_sample_folder, file_name)

            # Extract parts directly without using re.search
            try:
                video_number, start_time_str, end_time_str, fps_str = self.extract_parts(file_name)

                # Construct the new clip number
                clip_number = clip_number_counter
                clip_number_counter += 1

                new_name = f"video_{video_number}_clip_{clip_number}_{start_time_str}_to_{end_time_str}_{fps_str}fps.mp4"
                new_path = os.path.join(random_sample_folder, new_name)

                print(f"Renaming: {original_path} -> {new_path}")
                os.rename(original_path, new_path)
                print(f"Renamed: {original_path} -> {new_path}")
            except IndexError:
                print(f"Skipping file: {original_path} (does not match the expected pattern)")

        return {"message": "Video processing completed.", "output_path": self.output_path}, 200

    def get_video_clips(self, all_clips_folder):
        video_clips = {}

        for clip_name in os.listdir(all_clips_folder):
            if clip_name.startswith('video_'):
                video_number = int(clip_name.split('_')[1])  # Extract video number from the clip name
                if video_number not in video_clips:
                    video_clips[video_number] = []

                video_clips[video_number].append(clip_name)

        return video_clips
    
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

    def process_single_video(self, video_file, clip_length, fps, video_number):
        video_clip = VideoFileClip(video_file)
        video_duration = video_clip.duration

        num_clips = int(video_duration / clip_length)

        start_times = self.generate_start_times(video_duration, clip_length, num_clips)

        clips_folder = os.path.join(self.output_path, 'all_clips')
        os.makedirs(clips_folder, exist_ok=True)

        for i, start_time in enumerate(start_times):
            end_time = start_time + clip_length

            output_name = self.generate_output_name(video_number, i, start_time, end_time, fps)
            output_path = os.path.join(clips_folder, output_name)

            trimmed_clip = video_clip.subclip(start_time, end_time)

            trimmed_clip.write_videofile(output_path, codec="libx264", preset="ultrafast", threads=4, fps=fps, ffmpeg_params=["-pix_fmt", "yuv420p"])
            print(f"Processed: {video_file} -> {output_path}")

    def generate_start_times(self, video_duration, clip_length, num_clips):
        start_times = []
        for i in range(num_clips):
            start_time = i * clip_length
            start_times.append(start_time)
        return start_times

    @staticmethod
    def generate_output_name(video_number, clip_number, start_time, end_time, fps):
        start_time_str = VideoProcessor.time_to_str(start_time)
        end_time_str = VideoProcessor.time_to_str(end_time)

        return f"video_{video_number}_clip_{clip_number}_{start_time_str}_to_{end_time_str}_{fps}fps.mp4"

    @staticmethod
    def time_to_str(time):
        minutes, seconds = divmod(time, 60)
        return f"{int(minutes):02d}_{int(seconds):02d}"

processor = VideoProcessor()

@app.route('/process_and_sample', methods=['POST'])
def process_and_sample():
    data = request.form if request.form else request.json
    result, status_code = processor.process_and_sample(data)
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run(debug=True)
