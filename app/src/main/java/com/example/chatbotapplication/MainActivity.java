package com.example.chatbotapplication;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.Manifest;
import android.content.pm.PackageManager;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.Toast;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {
    ChatAdapter adapter;
    RecyclerView recyclerView;
    FrameLayout layoutSend, btnrecord;
    EditText etInputMsg;
    private MediaRecorder mediaRecorder;
    private MediaPlayer mediaPlayer;
    private String AudioSavePath = null;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
//        PyObject module = py.getModule("my_module");

        List<chatData> list_send = new ArrayList<>();
        list_send.add(new chatData("",
                "May 23, 2015",
                "Best Of Luck",0));
        list_send.add(new chatData("",
                "June 09, 2015",
                "Hello World",0));

//        list = getData();
        recyclerView = (RecyclerView) findViewById(R.id.chatRecyclerView);

        //sending adapter
        adapter = new ChatAdapter(list_send, getApplication());
        recyclerView.setAdapter(adapter);

        recyclerView.setLayoutManager(new LinearLayoutManager(MainActivity.this));

        layoutSend = (FrameLayout) findViewById(R.id.layoutSend);
        etInputMsg = (EditText) findViewById(R.id.inputMessage);
        btnrecord = (FrameLayout) findViewById(R.id.btnrecord);

        if (checkPermissions()){
            Log.d("Debug","permission already provided");
        }else{
            ActivityCompat.requestPermissions(MainActivity.this, new String[]{
                    Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE},1);
        }

        layoutSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d("Debug send click","send msg click btn pressed");
                String userinputstr = etInputMsg.getText().toString();
                Date c = Calendar.getInstance().getTime();
                SimpleDateFormat df = new SimpleDateFormat("MMM dd, yyyy", Locale.getDefault());
                String formattedDate = df.format(c);
                Log.d("Debug send click",formattedDate);
                list_send.add(new chatData("",
                        formattedDate,
                        ""+userinputstr,0));
                adapter = new ChatAdapter(list_send, getApplication());
                recyclerView.setAdapter(adapter);
                adapter.notifyDataSetChanged();

                etInputMsg.setText(""); //clear the textbox after user click send

                //get a reply upon entering text
                userinputstr = userinputstr.toLowerCase();
                if (userinputstr.contains("i want to report a vishing attack")) {
                    list_send.add(new chatData("", "", "What happened?", 1));
                    adapter.notifyDataSetChanged();
                } else if (userinputstr.contains("i want to check if i got vished")) {
                    list_send.add(new chatData("", "", "Ok! Send me an audio file for me to analyze.", 1));
                    adapter.notifyDataSetChanged();
                } else {
                    // Handle other user inputs and provide appropriate responses
                    // For example:
                    list_send.add(new chatData("", "", "I'm sorry, I don't understand. Can you please rephrase your question?", 1));
                    adapter.notifyDataSetChanged();
                }

            }
        });
        btnrecord.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()){
                    case MotionEvent.ACTION_DOWN:
                        //start recording
                        if (checkPermissions()){
                            AudioSavePath = Environment.getExternalStorageDirectory().getAbsolutePath()+"/"+"recordingAudio.mp3";
                            Log.d("Debug filepath",AudioSavePath);
                            mediaRecorder = new MediaRecorder();
                            mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
                            mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
                            mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
                            mediaRecorder.setOutputFile(AudioSavePath);

                            try {
                                mediaRecorder.prepare();
                                mediaRecorder.start();
                                Toast.makeText(MainActivity.this, "Recording started", Toast.LENGTH_SHORT).show();
                            }catch (IOException e){
                                e.printStackTrace();
                            }

                            //display media player
                            list_send.add(new chatData("",
                                    "",
                                    "",2));
                            adapter = new ChatAdapter(list_send, getApplication());
                            recyclerView.setAdapter(adapter);
                            adapter.notifyDataSetChanged();

//                            mediaPlayer = new MediaPlayer();
//                            try {
//                                mediaPlayer.setDataSource(AudioSavePath);
//                                mediaPlayer.prepare();
//                                mediaPlayer.start();
//                            } catch (IOException e) {
//                                throw new RuntimeException(e);
//                            }

                        }else{
                            ActivityCompat.requestPermissions(MainActivity.this, new String[]{
                                    Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE},1);
                        }
                        return true;
                    case MotionEvent.ACTION_UP:
                        //stop recording
                        if (mediaRecorder != null) {
                            try {
                                mediaRecorder.stop();
                                mediaRecorder.release();

                                //display media player
//                                list_send.add(new chatData("",
//                                        "",
//                                        "",2));
//                                adapter = new ChatAdapter(list_send, getApplication());
//                                recyclerView.setAdapter(adapter);
//                                adapter.notifyDataSetChanged();

                            } catch (IllegalStateException e) {
                                Log.d("debug recording stop function error",e.toString());
                            }
                            Toast.makeText(MainActivity.this, "Recording stopped", Toast.LENGTH_SHORT).show();
                        }
                        return true;
                }
                return false;
            }
        });
    }

    private boolean checkPermissions(){
        int audio_per = ActivityCompat.checkSelfPermission(getApplicationContext(), Manifest.permission.RECORD_AUDIO);
        int write_per = ActivityCompat.checkSelfPermission(getApplicationContext(), Manifest.permission.RECORD_AUDIO);
        return audio_per == PackageManager.PERMISSION_GRANTED && write_per == PackageManager.PERMISSION_GRANTED;
    }


}