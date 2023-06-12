package com.example.chatbotapplication;

public class chatData {
    String name;
    String date;
    String message;
    int viewtype;

    chatData(String name,
             String date,
             String message,
             int viewtype)
    {
        this.name = name;
        this.date = date;
        this.message = message;
        this.viewtype = viewtype;
    }
}