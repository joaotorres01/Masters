package com.example.gymbox_semaforo;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.drawable.DrawableCompat;

import android.content.res.AssetManager;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.List;
import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;


public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        List<String[]> dataRows = readCSV();

        ImageView imageViewLogo = findViewById(R.id.imageViewLogo);
        Drawable drawable_logo = ContextCompat.getDrawable(this, R.drawable.logo);
        imageViewLogo.setImageDrawable(drawable_logo);

        // Obter a hora atual
        Calendar now = Calendar.getInstance();
        int currentDay = now.get(Calendar.DAY_OF_WEEK);
        int currentHour = now.get(Calendar.HOUR_OF_DAY);
        int currentMinute = now.get(Calendar.MINUTE);

        // Obtenha as referências dos elementos da interface do usuário
        TextView textViewGymStatus = findViewById(R.id.textViewGymStatus);
        TextView textViewGymStatusMessage = findViewById(R.id.textViewGymStatusMessage);
        ImageView imageViewSemaphore = findViewById(R.id.imageViewSemaphore);

        if ((currentDay >= Calendar.MONDAY && currentDay <= Calendar.FRIDAY && currentHour >= 8 && (currentHour < 22 || (currentHour == 22 && currentMinute == 0)))
                || (currentDay == Calendar.SATURDAY && currentHour >= 9 && (currentHour < 18 || (currentHour == 18 && currentMinute == 0)))) {

            int entriesCount = 0;
            for (int i = 1; i < dataRows.size(); i++) {
                String[] row = dataRows.get(i);
                int entryDayOfWeek = getDayOfWeekFromString(row[6]);  // Supondo que o campo 'weekday' é o 7º campo
                int entryHour = Integer.parseInt(row[7]);             // Supondo que o campo 'hour' é o 8º campo

                // Comparar com o dia da semana e a hora atual
                if (entryDayOfWeek == currentDay && entryHour == currentHour) {
                    entriesCount++;
                }
            }

            // Definir a cor do semáforo
            String semaphoreColor;
            if (entriesCount >= 2200) {
                semaphoreColor = "RED";
            } else if (entriesCount >= 2000) {
                semaphoreColor = "YELLOW";
            } else {
                semaphoreColor = "GREEN";
            }

            // Definir a cor do semáforo no ImageView
            int colorResId;
            switch (semaphoreColor) {
                case "GREEN":
                    colorResId = R.color.green;
                    break;
                case "YELLOW":
                    colorResId = R.color.yellow;
                    break;
                case "RED":
                    colorResId = R.color.red;
                    break;
                default:
                    colorResId = R.color.green;
                    break;
            }

            Drawable drawable = ContextCompat.getDrawable(this, R.drawable.shape_semaphore);
            DrawableCompat.setTint(drawable, ContextCompat.getColor(this, colorResId));
            imageViewSemaphore.setImageDrawable(drawable);


            // Mostrar a mensagem de horário do ginásio
            String gymStatusMessage = "Ginásio aberto\n";
            String gymMessage = "A cor apresentada representa a lotação média do ginásio neste momento:\n-> Verde - Pouco populado;\n-> Amarelo - Lotação média;\n-> Vermelho - Lotação quase cheia.";
            textViewGymStatus.setText(gymStatusMessage);
            textViewGymStatusMessage.setText(gymMessage);


            // Agora você pode utilizar a variável 'semaphoreColor' para mostrar o semáforo na sua UI
        } else {
            // Ginásio não está aberto, ocultar o semáforo e mostrar mensagem e horário
            imageViewSemaphore.setVisibility(View.GONE);

            // Ginásio não está aberto, mostrar mensagem e horário
            String gymClosedMessage = "Ginásio fechado";
            textViewGymStatus.setText(gymClosedMessage);
        }
    }

    public List<String[]> readCSV() {
        List<String[]> rows = new ArrayList<>();
        AssetManager assetManager = getAssets();

        try {
            InputStream csvStream = assetManager.open("datagymbox_treated.csv");
            InputStreamReader csvStreamReader = new InputStreamReader(csvStream);
            CSVReader csvReader = new CSVReader(csvStreamReader);
            String[] nextLine;

            while ((nextLine = csvReader.readNext()) != null) {
                rows.add(nextLine);
            }
        } catch (IOException | CsvValidationException e) {
            e.printStackTrace();
        }
        return rows;
    }

    private int getDayOfWeekFromString(String weekday) {
        switch (weekday) {
            case "Sunday":
                return Calendar.SUNDAY;
            case "Monday":
                return Calendar.MONDAY;
            case "Tuesday":
                return Calendar.TUESDAY;
            case "Wednesday":
                return Calendar.WEDNESDAY;
            case "Thursday":
                return Calendar.THURSDAY;
            case "Friday":
                return Calendar.FRIDAY;
            case "Saturday":
                return Calendar.SATURDAY;
            default:
                return -1;  // Valor inválido
        }
    }


}