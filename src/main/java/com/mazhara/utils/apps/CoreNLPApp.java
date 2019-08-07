package com.mazhara.utils.apps;
import com.mazhara.utils.corenlp.SentimentTransformer;
import com.mazhara.utils.postre.PostgresUtils;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;


public class CoreNLPApp {

    public static void main(String[] args){

        Connection connection = PostgresUtils.connectToPostgres();

        String user = System.getenv("TWITTER_USER");
        System.out.println(user);

        PostgresUtils.cleanTextField(connection, user);

        ResultSet resultSet = PostgresUtils.getAllTweets(connection, user);
        SentimentTransformer transformer = new SentimentTransformer();
        try{
            while (resultSet.next()) {
                String tweet = resultSet.getString("clean_after_java_text");
                long id = resultSet.getLong("id");
                SentimentTransformer.SentimentValues values = transformer.getSentiment(tweet);
                PostgresUtils.insertSentiment(connection, user, values.getSentimentScore(), values.sentimentType, id);
            }
        }catch (SQLException e){
            System.out.println(e.getMessage());
        }


    }


}
