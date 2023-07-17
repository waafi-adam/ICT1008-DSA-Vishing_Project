package com.example.chatbotapplication;

import android.Manifest;
import android.content.ContentResolver;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Random;

public class MainActivity extends AppCompatActivity implements ChatAdapter.OnItemClickListener{
    private static final int PERMISSION_REQUEST_CODE = 1;
    private static final int REQUEST_CODE_SPEECH_INPUT = 1;
    ChatAdapter adapter;
    RecyclerView recyclerView;
    FrameLayout layoutSend, btnrecord;
    EditText etInputMsg;
    Button btnCheckResp, btnHelp;
    private MediaRecorder mediaRecorder;
    private String AudioSavePath = null;
    private String AudioSavePath_new = null;
    private String AudioFileName = null;
    List<chatData> list_send = new ArrayList<>();

    List<String> userResponses = new ArrayList<>();
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Date c = Calendar.getInstance().getTime();
        SimpleDateFormat df = new SimpleDateFormat("MMM dd, yyyy", Locale.getDefault());
        String formattedDate = df.format(c);
        list_send.add(new chatData("",
                formattedDate,
                "Hello, please enter your text to get the spam likelihood percentage",0));


        recyclerView = (RecyclerView) findViewById(R.id.chatRecyclerView);

        //sending adapter
        adapter = new ChatAdapter(list_send, getApplication());
        adapter.setOnItemClickListener(this);
        recyclerView.setAdapter(adapter);

        recyclerView.setLayoutManager(new LinearLayoutManager(MainActivity.this));

        layoutSend = (FrameLayout) findViewById(R.id.layoutSend);
        etInputMsg = (EditText) findViewById(R.id.inputMessage);
        btnrecord = (FrameLayout) findViewById(R.id.btnrecord);

        btnCheckResp = (Button) findViewById(R.id.btnChkRp);
        btnHelp = (Button) findViewById(R.id.btnHelp);

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

                //call get reply function
                getReply(userinputstr);

            }
        });
        btnCheckResp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String userinputstr = "Check Responses";
                list_send.add(new chatData("", "", ""+userinputstr, 0));
                adapter.notifyDataSetChanged();
                //call get reply function
                getReply(userinputstr);
            }
        });
        btnHelp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                list_send.add(new chatData("", "", "How does this app works?", 0));
                adapter.notifyDataSetChanged();

                list_send.add(new chatData("", "", "You may enter the text manually or use the speech to text feature by clicking on the record button on the bottom left. We will then take the text entered and display the percentage of the likelihood that the text is a spam message.", 1));
                adapter.notifyDataSetChanged();

            }
        });
        btnrecord.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()){
                    case MotionEvent.ACTION_DOWN:
                        //speech to text android version
                        startSpeechRecognition();
                        //

                        return true;
                    case MotionEvent.ACTION_UP:

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
        Log.d("debug speech to text filename: ",AudioFileName);

    }
    public void startSpeechRecognition() {

        //speech to text android version
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);

        // secret parameters that when added provide audio url in the result
        intent.putExtra("android.speech.extra.GET_AUDIO_FORMAT", "audio/AMR");
        intent.putExtra("android.speech.extra.GET_AUDIO", true);
        //

        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE,
                Locale.getDefault());
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak to text");

        try {
            startActivityForResult(intent, REQUEST_CODE_SPEECH_INPUT);
        }catch (Exception e) {
            Log.d("debug",e.toString());
        }


    }

    // handle result of speech recognition
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_SPEECH_INPUT) {
            if (resultCode == RESULT_OK && data != null) {
                // the resulting text is in the getExtras:
                Bundle bundle = data.getExtras();
                ArrayList<String> matches = bundle.getStringArrayList(RecognizerIntent.EXTRA_RESULTS);

                String userinputstr = matches.get(0).toString();
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

                getReply(userinputstr);

                // the recording url is in getData:
                Uri audioUri = data.getData();
                ContentResolver contentResolver = getContentResolver();
                try {
                    InputStream filestream = contentResolver.openInputStream(audioUri);
                } catch (FileNotFoundException e) {
                    throw new RuntimeException(e);
                }
                // TODO: read audio file from inputstream
            }
        }

    }
    public void getReply(String userinputstr){
        //get a reply upon entering text
        userinputstr = userinputstr.toLowerCase();
        if (userinputstr.contains("check responses")) {
            for (int i = 0; i < userResponses.size(); i++) {
                String userResponse = userResponses.get(i);

                // Add user's response to the list
                list_send.add(new chatData("", "", userResponse, 1));
                adapter.notifyDataSetChanged();
            }
        }else{
            userResponses.add(userinputstr);

            if (userinputstr.contains("i want to report a vishing attack")) {
                list_send.add(new chatData("", "", "What happened?", 1));
                adapter.notifyDataSetChanged();
            } else if (userinputstr.contains("i want to check if i got vished")) {
                list_send.add(new chatData("", "", "Ok! Send me an audio file for me to analyze.", 1));
                adapter.notifyDataSetChanged();
            } else {
                // Handle other user inputs and provide appropriate responses
                // For example:
//            list_send.add(new chatData("", "", "I'm sorry, I don't understand. Can you please rephrase your question?", 1));
//            adapter.notifyDataSetChanged();

                //get vishing prediction
                vishingprediction(userinputstr);

            }

        }

    }

    public void vishingprediction(String userinputstr){
        //get vishing prediction
        Python py = Python.getInstance();
        PyObject speech_to_text_module = py.getModule("Trie_Tree_vishing_detector");
        Float stt_output = speech_to_text_module.callAttr("trieTree",""+userinputstr).toJava(Float.class);
        Log.d("debug speech to text",""+stt_output);
        list_send.add(new chatData("", "", "Spam Likelihood: "+String.format("%.2f", stt_output)+"%", 1));
        adapter.notifyDataSetChanged();
    }

}