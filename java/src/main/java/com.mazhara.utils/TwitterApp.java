package com.mazhara.utils;

import com.mazhara.utils.corenlp.SentimentTransformer;
import com.mazhara.utils.postresql.PostgresUtils;
import com.mazhara.utils.twitter.TwitterUtils;
import twitter4j.Twitter;
import twitter4j.TwitterFactory;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;


public class TwitterApp {

    public static void main(String[] args){

        Twitter twitter = new TwitterFactory(TwitterUtils.getConfigs()).getInstance();

        String user1 = System.getenv("USER1");
        String user2 = System.getenv("USER2");

        System.out.println("User 1: "+user1);
        System.out.println("User 2: "+user2);

        Connection connection = PostgresUtils.connectToPostgres();


        PostgresUtils.createTable(connection, user1);
        PostgresUtils.createTable(connection, user2);

        TwitterUtils.storeUserTweets(twitter, user1, 1000, connection, user2);
        TwitterUtils.storeUserTweets(twitter, user2, 1000, connection, user1);

        PostgresUtils.cleanTextField(connection, user1);
        PostgresUtils.cleanTextField(connection, user2);

        TwitterApp.getAndInsertSentiment(connection, user1);
        TwitterApp.getAndInsertSentiment(connection, user2);


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
