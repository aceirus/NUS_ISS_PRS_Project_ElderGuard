package com.example.elderguardapp;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.ml.vision.FirebaseVision;
import com.google.firebase.ml.vision.common.FirebaseVisionImage;
import com.google.firebase.ml.vision.text.FirebaseVisionText;
import com.google.firebase.ml.vision.text.FirebaseVisionTextRecognizer;
import com.google.gson.JsonObject;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import okhttp3.ResponseBody;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MainActivity extends AppCompatActivity {
    ImageView imageView;
    EditText textMsgEd;
    TextView predictResponse;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //find_imageview
        imageView = findViewById(R.id.imageId);
        imageView.setVisibility(View.GONE);

        //find sms_or_image_text
        textMsgEd = findViewById(R.id.textmsgId);
        // find predictResp
        predictResponse = findViewById((R.id.predicttvId));

        //check app level permission is granted for camera, sms and internet
        if (checkSelfPermission(Manifest.permission.INTERNET) != PackageManager.PERMISSION_GRANTED){
            //grant the permission
            requestPermissions(new String[]{Manifest.permission.INTERNET},104);
        }

    }

    public void clearText(){
        textMsgEd.setText("");
        predictResponse.setText("");
    }

    public void doReadSMS(View view){
        if (checkSelfPermission(Manifest.permission.READ_SMS) != PackageManager.PERMISSION_GRANTED){
            //grant the permission
            requestPermissions(new String[]{Manifest.permission.READ_SMS},103);
        }
        clearText();
        imageView.setVisibility(View.GONE);
        @SuppressLint("Recycle") Cursor cursor = getContentResolver().query(Uri.parse("content://sms"),null,null,null,null);
        cursor.moveToFirst();
        textMsgEd.setText(cursor.getString(12));
    }

    public void tpConverter(View view){
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED){
            //grant the permission
            requestPermissions(new String[]{Manifest.permission.CAMERA},101);
        }
        clearText();
        //open the camera
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(intent, 101);
    }

    public void spConverter(View view){
        if (checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED){
            //grant the permission
            requestPermissions(new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},102);
        }
        clearText();
        //open the gallery
        Intent intent = new Intent(Intent.ACTION_PICK);
        intent.setType("image/*");
        startActivityForResult(intent, 102);
    }

    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data){
        imageView.setVisibility(View.VISIBLE);
        super.onActivityResult(requestCode, resultCode, data);
        Bitmap bitmap = null;
        //Take Pic
        if (resultCode == Activity.RESULT_OK && requestCode == 101) {
            Bundle bundle = data.getExtras();
            //from Bundle, extract image
            bitmap = (Bitmap) bundle.get("data");
            //set image in imageView
            imageView.setImageBitmap(bitmap);
        }
        //SelectPic
        else if (requestCode == 102 && resultCode == RESULT_OK){
            Uri imageUri = data.getData();
            try {
                bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(),imageUri);
            } catch (IOException e) {
                e.printStackTrace();
            }
            //set image in imageView
            imageView.setImageBitmap(bitmap);
        }
        //process the image to extract text
        //1. Create a firebaseVision image object from a bitmap object
        FirebaseVisionImage firebaseVisionImage = FirebaseVisionImage.fromBitmap(bitmap);
        //2. Get an instance of FirebaseVision Image
        FirebaseVision firebaseVision = FirebaseVision.getInstance();
        //3. Create an instance of FirebaseVisionTextRecognizer
        FirebaseVisionTextRecognizer firebaseVisionTextRecognizer = firebaseVision.getOnDeviceTextRecognizer();
        //4. Create a task to process the image
        Task<FirebaseVisionText> task = firebaseVisionTextRecognizer.processImage(firebaseVisionImage);
        //5. if task is success
        task.addOnSuccessListener(new OnSuccessListener<FirebaseVisionText>() {
            @Override
            public void onSuccess(FirebaseVisionText firebaseVisionText) {
                String textMsg = firebaseVisionText.getText();
                textMsgEd.setText(textMsg);
            }
        });
        //6. if task is failure
        task.addOnFailureListener(new OnFailureListener() {
            @Override
            public void onFailure(@NonNull Exception e) {
                Toast.makeText(getApplicationContext(), e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void postRequest(String updatedMsg) {
        if (!updatedMsg.equals("")) {
            OkHttpClient client = new OkHttpClient();
            String elg_url = "https://elderguard.herokuapp.com/predict";
            // POST
            JsonObject postData = new JsonObject();
            postData.addProperty("txt", updatedMsg);

            final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
            RequestBody postBody = RequestBody.create(JSON, postData.toString());
            //create post request
            Request postreq = new Request.Builder()
                    .url(elg_url)
                    .post(postBody)
                    .build();

            client.newCall(postreq).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    e.printStackTrace();
                }

                @Override
                public void onResponse(Call call, Response response) {
                    try {
                        ResponseBody responseBody = response.body();
                        String responseString = responseBody.string();
                        if (!response.isSuccessful()) {
                            throw new IOException("Unexpected code " + response);
                        }
//                        Pattern
//                        String final_predict_res = null;

                        MainActivity.this.runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                String pattern = ".(final_predict).:..(.)";
                                String final_predict_res=null;
                                Matcher m = Pattern.compile(pattern).matcher(responseString);
                                if (m.find()){
                                    final_predict_res = m.group().substring(17,18); //19 "final_predict":"1"
                                }
                                predictResponse.setText(responseString);
                                if (final_predict_res.equals("1")){
                                    imageView.setImageResource(R.drawable.redcross);
                                    imageView.setVisibility(View.VISIBLE);
                                } else if (final_predict_res.equals("0")){
                                    imageView.setImageResource(R.drawable.greentick);
                                    imageView.setVisibility(View.VISIBLE);
                                } else {
                                    imageView.setImageResource(R.drawable.unknown);
                                    imageView.setVisibility(View.VISIBLE);
                                }

                            }
                        });
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
        }

    }

    public void doPredict(View view){
        String updatedMsg = textMsgEd.getText().toString();
        if (!updatedMsg.equals("")) {
            postRequest(updatedMsg);
        }
        else {
            clearText();
            imageView.setVisibility(View.GONE);
        }
    }

}

