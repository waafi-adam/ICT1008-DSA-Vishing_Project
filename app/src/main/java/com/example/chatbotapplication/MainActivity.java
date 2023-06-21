package com.example.chatbotapplication;

import androidx.annotation.NonNull;
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
import android.os.Handler;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewConfiguration;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.SeekBar;
import android.widget.Toast;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Random;

public class MainActivity extends AppCompatActivity implements ChatAdapter.OnItemClickListener{
    private static final int PERMISSION_REQUEST_CODE = 1;
    ChatAdapter adapter;
    RecyclerView recyclerView;
    FrameLayout layoutSend, btnrecord;
    EditText etInputMsg;
    private MediaRecorder mediaRecorder;
    private String AudioSavePath = null;
    Random random ;
    String RandomAudioFileName = "ABCDEFGHIJKLMNOP";

    List<String> userResponses = new ArrayList<>();
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

        recyclerView = (RecyclerView) findViewById(R.id.chatRecyclerView);

        //sending adapter
        adapter = new ChatAdapter(list_send, getApplication());
        adapter.setOnItemClickListener(this);
        recyclerView.setAdapter(adapter);

        recyclerView.setLayoutManager(new LinearLayoutManager(MainActivity.this));

        layoutSend = (FrameLayout) findViewById(R.id.layoutSend);
        etInputMsg = (EditText) findViewById(R.id.inputMessage);
        btnrecord = (FrameLayout) findViewById(R.id.btnrecord);

        if (checkPermissions()){
            Log.d("Debug","permission already provided");
        }else{
            requestPermissions();
        }

        layoutSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d("Debug send click", "send msg click btn pressed");
                String userinputstr = etInputMsg.getText().toString();
                Date c = Calendar.getInstance().getTime();
                SimpleDateFormat df = new SimpleDateFormat("MMM dd, yyyy", Locale.getDefault());
                String formattedDate = df.format(c);
                Log.d("Debug send click", formattedDate);
                list_send.add(new chatData("",
                        formattedDate,
                        "" + userinputstr, 0));
                adapter = new ChatAdapter(list_send, getApplication());
                recyclerView.setAdapter(adapter);
                adapter.notifyDataSetChanged();

                etInputMsg.setText(""); //clear the textbox after user click send

                //get a reply upon entering text
                userinputstr = userinputstr.toLowerCase();
                userResponses.add(userinputstr);
                if (userinputstr.contains("i want to report a vishing attack")) {
                    list_send.add(new chatData("", "", "What happened?", 1));
                    adapter.notifyDataSetChanged();
                } else if (userinputstr.contains("i want to check if i got vished")) {
                    list_send.add(new chatData("", "", "Ok! Send me an audio file for me to analyze.", 1));
                    adapter.notifyDataSetChanged();
                } else if (userinputstr.contains("check responses")) {
                    for (int i = 0; i < userResponses.size(); i++) {
                        String userResponse = userResponses.get(i);

                        // Add user's response to the list
                        list_send.add(new chatData("", "", userResponse, 1));
                        adapter.notifyDataSetChanged();
                    }
                } else {
                    // Handle other user inputs and provide appropriate responses
                    // For example:
                    list_send.add(new chatData("", "", "I'm sorry, I don't understand. Can you please rephrase your question?", 1));
                    adapter.notifyDataSetChanged();
                }

            }
        });
        btnrecord.setOnTouchListener(new View.OnTouchListener() {
            private final Handler handler = new Handler();
            private final Runnable runnable = new Runnable() {
                @Override
                public void run() {
                    //start recording
                    if (checkPermissions()){
                        // Create a timestamped file name
                        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
                        String fileName = "Recording_" + timeStamp + ".3gp";

                        // Get the app's private external storage directory
                        File externalFilesDir = getExternalFilesDir(null);
                        if (externalFilesDir != null) {
                            // Create a directory for recordings if it doesn't exist
                            File recordingsDir = new File(externalFilesDir, "Recordings");
                            recordingsDir.mkdirs();

                            // Create the record file
                            File recordFile = new File(recordingsDir, fileName);
                            AudioSavePath = recordFile.getAbsolutePath(); //file location: /storage/emulated/0/Android/data/com.example.chatbotapplication/files/Recordings/

                            // Initialize and configure the MediaRecorder
                            mediaRecorder = new MediaRecorder();
                            mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
                            mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
                            mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);
                            mediaRecorder.setOutputFile(AudioSavePath);

                            try {
                                mediaRecorder.prepare();
                                mediaRecorder.start();
                                Toast.makeText(MainActivity.this, "Recording started", Toast.LENGTH_SHORT).show();
                            } catch (IOException e) {
                                e.printStackTrace();
                                Toast.makeText(MainActivity.this, "Recording failed", Toast.LENGTH_SHORT).show();
                            }
                        }

                    }else{
                        requestPermissions();
                    }
                }
            };
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()){
                    case MotionEvent.ACTION_DOWN:
                        mediaRecorder = null;
                        handler.postDelayed(runnable, 1000);
                        return true;
                    case MotionEvent.ACTION_UP:
                        //stop recording
                        if (mediaRecorder != null) {
                            try {
                                mediaRecorder.stop();
                                mediaRecorder.release();
                                mediaRecorder = null;
                                Toast.makeText(MainActivity.this, "Recording stopped", Toast.LENGTH_SHORT).show();

                                //display media player
                                list_send.add(new chatData("", "", ""+AudioSavePath, 2));
                                adapter.notifyDataSetChanged();


                            } catch (IllegalStateException e) {
                                Log.d("debug recording stop function error",e.toString());
                            }
                        }
                        return true;
                }
                return false;
            }
        });
    }

    private boolean checkPermissions(){
        int audio_per = ActivityCompat.checkSelfPermission(getApplicationContext(), Manifest.permission.RECORD_AUDIO);
        int write_per = ActivityCompat.checkSelfPermission(getApplicationContext(), Manifest.permission.WRITE_EXTERNAL_STORAGE);
        return audio_per == PackageManager.PERMISSION_GRANTED && write_per == PackageManager.PERMISSION_GRANTED;
    }
    private void requestPermissions() {
        ActivityCompat.requestPermissions(MainActivity.this, new String[]{
                Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE},PERMISSION_REQUEST_CODE);
    }
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED &&
                    grantResults[1] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Permissions granted", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Permissions denied", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    public void onItemClick(int position) {
        //play recording

    }
}