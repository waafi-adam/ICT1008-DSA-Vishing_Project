package com.example.chatbotapplication;

import android.content.Context;
import android.media.MediaPlayer;
import android.os.Handler;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.SeekBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

public class ChatAdapter extends RecyclerView.Adapter<chatViewHolder> implements MediaPlayer.OnCompletionListener{
    List<chatData> list = Collections.emptyList();
    Context context;
    private static final int VIEW_TYPE_SENT = 0;
    private static final int VIEW_TYPE_RECEIVED = 1;

    private static final int VIEW_TYPE_MP = 2;
    private OnItemClickListener listener;
    private boolean checkpause = false;
    public int playingposition = -1;
    private Handler handler;
    private Runnable runnable;

    private MediaPlayer mediaPlayer;

    public ChatAdapter(List<chatData> list, Context context){
        this.list = list;
        this.context = context;
    }


    public static class ViewHolder extends RecyclerView.ViewHolder{
        private final TextView textViewMsg, textViewDT;
        public ViewHolder(View view){
            super(view);
            textViewMsg = (TextView) view.findViewById(R.id.textMessage);
            textViewDT = (TextView) view.findViewById(R.id.textDateTime);
        }
        public TextView getTextView(){
            return textViewMsg;
        }
    }
    public class ViewHolderMediaPlayer extends RecyclerView.ViewHolder{
        public ViewHolderMediaPlayer(View view){
            super(view);
        }
    }

    @NonNull
    @Override
    public chatViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        Context context = parent.getContext();
        LayoutInflater inflater = LayoutInflater.from(context);
        switch(viewType){
            case VIEW_TYPE_SENT:
                View photoView = inflater.inflate(R.layout.item_container_sent_message, parent, false);
                chatViewHolder viewHolder = new chatViewHolder(photoView);
                return viewHolder;
            case VIEW_TYPE_RECEIVED:
                View receiveView = inflater.inflate(R.layout.item_container_received_message, parent, false);
                chatViewHolder viewHolder_r = new chatViewHolder(receiveView);
                return viewHolder_r;
            case VIEW_TYPE_MP:
                View mp_view = inflater.inflate(R.layout.item_container_media_player, parent, false);
                chatViewHolder viewHolder_mp = new chatViewHolder(mp_view);
                return viewHolder_mp;
            default:
                View defaultView = inflater.inflate(R.layout.item_container_sent_message, parent, false);
                chatViewHolder defaultviewHolder = new chatViewHolder(defaultView);
                return defaultviewHolder;
        }
    }

    @Override
    public void onBindViewHolder(final chatViewHolder holder, int position) {
        final int index = holder.getAdapterPosition();
        switch (holder.getItemViewType()) {
            case VIEW_TYPE_SENT:
                chatViewHolder viewHolder0 = (chatViewHolder)holder;
                viewHolder0.userMessage.setText(list.get(position).message);
                viewHolder0.msgSentDate.setText(list.get(position).date);
                break;
            case VIEW_TYPE_RECEIVED:
                chatViewHolder viewHolder1 = (chatViewHolder)holder;
                viewHolder1.userMessage.setText(list.get(position).message);
                viewHolder1.msgSentDate.setText(list.get(position).date);
                break;
            case VIEW_TYPE_MP:
                chatViewHolder viewHoldermp = (chatViewHolder)holder;
                //get audio file path
                String filepath = list.get(position).message;
                Log.d("debug audio",filepath);
                if (viewHoldermp.seekbar.getProgress() == 0){
                    viewHoldermp.button.setImageResource(R.drawable.ic_action_play);
                    checkpause = false;
                }else{
                    viewHoldermp.button.setImageResource(R.drawable.ic_action_pause);
                    checkpause = false;
                }
                viewHoldermp.button.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        Log.d("debug audio btn","pause: "+checkpause);
                        if (checkpause == false){
                            viewHoldermp.button.setImageResource(R.drawable.ic_action_pause);
                            checkpause = true;
                        }else{
                            viewHoldermp.button.setImageResource(R.drawable.ic_action_play);
                            checkpause = false;
                        }
                        //play recording
                        MediaPlayer mediaPlayer = new MediaPlayer();
                        try {
                            mediaPlayer.setDataSource(filepath);
                            mediaPlayer.prepare();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        // Initialize the SeekBar and setup progress updates
                        handler = new Handler();

                        mediaPlayer.setOnPreparedListener(new MediaPlayer.OnPreparedListener() {
                            @Override
                            public void onPrepared(MediaPlayer mediaPlayer) {
                                // Set the maximum value of the SeekBar to the audio duration
//                                viewHoldermp.button.setImageResource(R.drawable.ic_action_pause);
                                viewHoldermp.seekbar.setMax(mediaPlayer.getDuration());
                                checkpause = false;
                                // Start updating the SeekBar progress
                                if (mediaPlayer != null) {
                                    // Update the SeekBar progress with the current position
                                    viewHoldermp.seekbar.setProgress(mediaPlayer.getCurrentPosition());
                                    // Delayed call to update the SeekBar progress every second
                                    handler.postDelayed(runnable, 1000);
                                }
                            }
                        });

                        viewHoldermp.seekbar.setOnTouchListener(new View.OnTouchListener() {
                            @Override
                            public boolean onTouch(View view, MotionEvent motionEvent) {
                                return true;
                            }
                        });
                        // SeekBar change listener
                        viewHoldermp.seekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                            @Override
                            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                                if (fromUser) {
                                    // Seek to the selected progress when the user drags the SeekBar
                                    mediaPlayer.seekTo(progress);
                                }
                                if (progress == seekBar.getMax()) {
                                    viewHoldermp.button.setImageResource(R.drawable.ic_action_play);
                                    seekBar.setProgress(0);
                                }
                            }

                            @Override
                            public void onStartTrackingTouch(SeekBar seekBar) {
                                // Remove the callback to stop updating the SeekBar progress
                                handler.removeCallbacks(runnable);
                            }

                            @Override
                            public void onStopTrackingTouch(SeekBar seekBar) {
                                // Resume updating the SeekBar progress
                                if (mediaPlayer != null) {
                                    // Update the SeekBar progress with the current position
                                    viewHoldermp.seekbar.setProgress(mediaPlayer.getCurrentPosition());
                                    // Delayed call to update the SeekBar progress every second
                                    handler.postDelayed(runnable, 1000);
                                }
                            }
                        });
                        // Set up the runnable for updating the SeekBar progress
                        runnable = new Runnable() {
                            @Override
                            public void run() {
                                if (mediaPlayer != null) {
                                    // Update the SeekBar progress with the current position
                                    viewHoldermp.seekbar.setProgress(mediaPlayer.getCurrentPosition());
                                    // Delayed call to update the SeekBar progress every second
                                    handler.postDelayed(runnable, 1000);
                                }

                            }
                        };
                        //

                        mediaPlayer.start();

                        if (listener != null) {
                            listener.onItemClick(viewHoldermp.getAdapterPosition());

                        }
                    }
                });
                break;
        }
    }


//    private void initializeSeekBar() {
//
//
//    }

//    private void updateSeekBar() {
//
//    }

    // ...

    @Override
    public void onCompletion(MediaPlayer mediaPlayer) {
        // Stop updating the SeekBar progress when audio playback finishes
        handler.removeCallbacks(runnable);
//        seekBar.setProgress(0);
    }


    @Override
    public int getItemViewType(int position) {
        Object item = list.get(position);
        Log.d("debug item",list.get(position).viewtype+"");
        // Determine the view type based on the item's class
        if (list.get(position).viewtype == 0) {
            return VIEW_TYPE_SENT;
        } else if (list.get(position).viewtype == 1) {
            return VIEW_TYPE_RECEIVED;
        }else if (list.get(position).viewtype == 2) {
            return VIEW_TYPE_MP;
        }
        throw new IllegalArgumentException("Invalid item type at position: " + position);
    }


    @Override
    public int getItemCount() {
        return list.size();
    }
    @Override
    public void onAttachedToRecyclerView(RecyclerView recyclerView) {
        super.onAttachedToRecyclerView(recyclerView);
    }
    public interface OnItemClickListener {
        void onItemClick(int position);
    }
    public void setOnItemClickListener(OnItemClickListener listener) {
        this.listener = listener;
    }


}
