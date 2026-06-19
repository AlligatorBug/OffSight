/**
 * Reads the intrinsic pixel dimensions of a video file without uploading it.
 * The backend sends bbox coordinates in raw pixel space (frame.shape), but
 * never tells the frontend the frame size — so we read it straight off the
 * File object using a throwaway <video> element before the socket opens.
 */
export function getVideoDimensions(file) {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    video.preload = 'metadata';

    video.onloadedmetadata = () => {
      const dims = { width: video.videoWidth, height: video.videoHeight };
      URL.revokeObjectURL(video.src);
      resolve(dims);
    };

    video.onerror = () => {
      URL.revokeObjectURL(video.src);
      reject(new Error('Could not read video metadata'));
    };

    video.src = URL.createObjectURL(file);
  });
}