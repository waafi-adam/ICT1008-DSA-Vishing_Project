package com.example.chatbotapplication;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.FragmentTransaction;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.FrameLayout;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {
    ChatAdapter adapter;
    RecyclerView recyclerView;
    private PreferenceManager preferenceManager;
    FrameLayout layoutSend;
    EditText etInputMsg;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
//        PyObject module = py.getModule("my_module");

        List<chatData> list = new ArrayList<>();
        list.add(new chatData("",
                "May 23, 2015",
                "Best Of Luck"));
        list.add(new chatData("",
                "June 09, 2015",
                "Hello World"));

//        list = getData();
        recyclerView = (RecyclerView) findViewById(R.id.chatRecyclerView);
        adapter = new ChatAdapter(list, getApplication());
        recyclerView.setAdapter(adapter);
        recyclerView.setLayoutManager(new LinearLayoutManager(MainActivity.this));

        layoutSend = (FrameLayout) findViewById(R.id.layoutSend);
        etInputMsg = (EditText) findViewById(R.id.inputMessage);
        layoutSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d("Debug send click","send msg click btn pressed");
                String userinputstr = etInputMsg.getText().toString();
                Log.d("Debug send click",userinputstr);
                Date currentTime = Calendar.getInstance().getTime();
                Log.d("Debug send click", currentTime.toString());
                Date c = Calendar.getInstance().getTime();
                SimpleDateFormat df = new SimpleDateFormat("MMM dd, yyyy", Locale.getDefault());
                String formattedDate = df.format(c);
                Log.d("Debug send click",formattedDate);
                list.add(new chatData("",
                        formattedDate,
                        ""+userinputstr));
                adapter = new ChatAdapter(list, getApplication());
                recyclerView.setAdapter(adapter);
                adapter.notifyDataSetChanged();
            }
        });
    }
//    private void sendMessage(){
//        HashMap<String, Object> message = new HashMap<>();
//        message.put(Constants.KEY_SENDER_ID,preferenceManager);
//    }


}