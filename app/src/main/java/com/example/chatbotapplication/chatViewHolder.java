package com.example.chatbotapplication;

import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.SeekBar;
import android.widget.TextView;

import androidx.recyclerview.widget.RecyclerView;

public class chatViewHolder
        extends RecyclerView.ViewHolder {
    TextView userName;
    TextView userMessage;
    TextView msgSentDate;
    View view;
    ImageButton button;
    SeekBar seekbar;

    chatViewHolder(View itemView)
    {
        super(itemView);
        userMessage
                = (TextView)itemView
                .findViewById(R.id.textMessage);
        msgSentDate
                = (TextView)itemView
                .findViewById(R.id.textDateTime);
        button = (ImageButton) itemView.findViewById(R.id.ibPlay);
        seekbar = (SeekBar) itemView.findViewById(R.id.seekBar);
        view  = itemView;
    }
}