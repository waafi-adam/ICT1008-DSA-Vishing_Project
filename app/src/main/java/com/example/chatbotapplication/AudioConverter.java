package com.example.chatbotapplication;
import android.media.MediaCodec;
import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.media.MediaMuxer;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;

public class AudioConverter {
    public static void convert3gpToWav(String inputPath, String outputPath) {
        try {
            MediaExtractor extractor = new MediaExtractor();
            extractor.setDataSource(inputPath);

            int audioTrackIndex = getAudioTrackIndex(extractor);
            extractor.selectTrack(audioTrackIndex);

            MediaFormat audioFormat = extractor.getTrackFormat(audioTrackIndex);
            MediaCodec codec = MediaCodec.createDecoderByType(audioFormat.getString(MediaFormat.KEY_MIME));
            codec.configure(audioFormat, null, null, 0);
            codec.start();

            MediaMuxer muxer = new MediaMuxer(outputPath, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
            int audioTrack = muxer.addTrack(audioFormat);
            muxer.start();

            final int TIMEOUT_US = 10000;
            MediaCodec.BufferInfo info = new MediaCodec.BufferInfo();
            ByteBuffer[] codecInputBuffers = codec.getInputBuffers();
            ByteBuffer[] codecOutputBuffers = codec.getOutputBuffers();

            boolean sawInputEOS = false;
            boolean sawOutputEOS = false;

            while (!sawOutputEOS) {
                if (!sawInputEOS) {
                    int inputBufferIndex = codec.dequeueInputBuffer(TIMEOUT_US);
                    if (inputBufferIndex >= 0) {
                        ByteBuffer inputBuffer = codecInputBuffers[inputBufferIndex];
                        int sampleSize = extractor.readSampleData(inputBuffer, 0);

                        if (sampleSize < 0) {
                            codec.queueInputBuffer(inputBufferIndex, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                            sawInputEOS = true;
                        } else {
                            long presentationTimeUs = extractor.getSampleTime();
                            codec.queueInputBuffer(inputBufferIndex, 0, sampleSize, presentationTimeUs, 0);
                            extractor.advance();
                        }
                    }
                }

                int outputBufferIndex = codec.dequeueOutputBuffer(info, TIMEOUT_US);
                if (outputBufferIndex >= 0) {
                    ByteBuffer outputBuffer = codecOutputBuffers[outputBufferIndex];
                    muxer.writeSampleData(audioTrack, outputBuffer, info);
                    codec.releaseOutputBuffer(outputBufferIndex, false);
                    if ((info.flags & MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0) {
                        sawOutputEOS = true;
                    }
                }
            }

            muxer.stop();
            muxer.release();
            codec.stop();
            codec.release();
            extractor.release();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static int getAudioTrackIndex(MediaExtractor extractor) {
        int numTracks = extractor.getTrackCount();
        for (int i = 0; i < numTracks; i++) {
            MediaFormat format = extractor.getTrackFormat(i);
            String mime = format.getString(MediaFormat.KEY_MIME);
            if (mime.startsWith("audio/")) {
                return i;
            }
        }
        return -1;
    }
}
