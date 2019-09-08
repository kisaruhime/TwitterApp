package com.mazhara.utils.apps;
import com.mazhara.utils.corenlp.SentimentTransformer;
import com.mazhara.utils.postre.PostgresUtils;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;


public class CoreNLPApp {

    public static void main(String[] args){

        Connection connection = PostgresUtils.connectToPostgres();

        String user1 = System.getenv("USER1");
        String user2 = System.getenv("USER2");

        System.out.println("User 1: "+user1);
        System.out.println("User 2: "+user2);

        PostgresUtils.cleanTextField(connection, user1);
        PostgresUtils.cleanTextField(connection, user2);

        CoreNLPApp.getAndInsertSentiment(connection, user1);
        CoreNLPApp.getAndInsertSentiment(connection, user2);


    }

    public static void getAndInsertSentiment(Connection connection, String user){

        ResultSet resultSet = PostgresUtils.getAllTweets(connection, user);
        SentimentTransformer transformer = new SentimentTransformer();
        try{
            while (resultSet.next()) {
                String tweet = resultSet.getString("clean_text");
                long id = resultSet.getLong("id");
                SentimentTransformer.SentimentValues values = transformer.getSentiment(tweet);
                PostgresUtils.insertSentiment(connection, user, values.getSentimentScore(), values.sentimentType, id);
            }
        }catch (SQLException e){
            System.out.println(e.getMessage());
        }

    }


}
