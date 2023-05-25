package com.example.chatbotapplication;

import android.view.View;
import android.widget.TextView;

import androidx.recyclerview.widget.RecyclerView;

public class chatViewHolder
        extends RecyclerView.ViewHolder {
    TextView userName;
    TextView userMessage;
    TextView msgSentDate;
    View view;

    chatViewHolder(View itemView)
    {
        super(itemView);
//        userName
//                = (TextView)itemView
//                .findViewById(R.id.textMessageSent);
        userMessage
                = (TextView)itemView
                .findViewById(R.id.textMessageSent);
        msgSentDate
                = (TextView)itemView
                .findViewById(R.id.textDateTimeSent);
        view  = itemView;
    }
}