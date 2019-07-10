package com.mazhara.utils.apps;

import com.mazhara.utils.corenlp.SentimentTransformer;
import com.mazhara.utils.postre.PostgresUtils;
import com.mazhara.utils.prepocess.TextUtils;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class CoreNLPApp {

    public static void main(String[] args){
        Connection connection = PostgresUtils.connectToPostgres();

        String user = System.getenv("TWITTER_USER");
        System.out.println(user);

        ResultSet resultSet = PostgresUtils.getAllTweets(connection, user);
        List<Object> list = new ArrayList<Object>();
        SentimentTransformer transformer = new SentimentTransformer();
        try{
            while (resultSet.next()) {
                String tweet = resultSet.getString("text");
                long id = resultSet.getLong("id");
                SentimentTransformer.SentimentValues values = transformer.getSentiment(tweet);
                PostgresUtils.insertSentiment(connection, user, values.getSentimentScore(), values.sentimentType, id);
            }
        }catch (SQLException e){
            System.out.println(e.getMessage());
        }


    }


}
