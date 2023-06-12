package com.example.chatbotapplication;

import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.Collections;
import java.util.List;

public class ChatAdapter extends RecyclerView.Adapter<chatViewHolder> {
    List<chatData> list = Collections.emptyList();
    Context context;
    private static final int VIEW_TYPE_SENT = 0;
    private static final int VIEW_TYPE_RECEIVED = 1;

    private static final int VIEW_TYPE_MP = 2;

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
    public void onBindViewHolder(final chatViewHolder holder, final int position) {
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
                viewHoldermp.userMessage.setText("");
                break;
        }
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
}
