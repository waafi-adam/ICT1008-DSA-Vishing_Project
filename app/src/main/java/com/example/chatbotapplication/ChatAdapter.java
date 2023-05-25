package com.example.chatbotapplication;

import android.content.Context;
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

    @NonNull
    @Override
    public chatViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        Context context = parent.getContext();
        LayoutInflater inflater = LayoutInflater.from(context);
        View photoView = inflater.inflate(R.layout.item_container_sent_message, parent, false);
        chatViewHolder viewHolder = new chatViewHolder(photoView);
        return viewHolder;
    }

    @Override
    public void onBindViewHolder(final chatViewHolder holder, final int position) {
        final int index = holder.getAdapterPosition();
//        holder.userName.setText(list.get(position).name);
        holder.userMessage.setText(list.get(position).message);
        holder.msgSentDate.setText(list.get(position).date);
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
