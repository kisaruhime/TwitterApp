package com.mazhara.utils.postresql;


import com.mazhara.utils.preprocess.TextUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import twitter4j.Status;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class PostgresUtils {

    static Logger LOGGER = LoggerFactory.getLogger(PostgresUtils.class);


    public static List<String> getCredentials(){

        final String urlDB = System.getenv("POSTGRES_URL");
        final String userDB = System.getenv("POSTGRES_USER");
        final String passwordDB = System.getenv("POSTGRES_PASSWORD");
        return  new ArrayList() {{
            add(urlDB);
            add(userDB);
            add(passwordDB);
        }};
    }


    public static Connection connectToPostgres()  {
        Connection conn = null;
        try {
            List<String> creds = getCredentials();
            conn = DriverManager.getConnection(creds.get(0), creds.get(1), creds.get(2));
            LOGGER.info("Connected to the PostgreSQL server successfully.");
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        return conn;
    }


    //TODO: change score col type to show double values
    public static void createTable(Connection conn, String user){
        try{
            String tweets = String.format("DROP TABLE IF EXISTS tweets_from_%s; CREATE TABLE  " +
                    "tweets_from_%s " +
                    "(id NUMERIC NOT NULL PRIMARY KEY, text varchar(280) NOT NULL," +
                    "clean_text varchar(280), CoreNLP_mark int, CoreNLP_sentiment varchar(20)," +
                    "vader_mark int, vader_sentiment varchar(20)," +
                    "svmclassifier_mark int, svmclassifier_sentiment varchar(20), " +
                    "mbclassifier_mark int, mbclassifier_sentiment varchar(20), " +
                    "lstm_mark int, lstm_sentiment varchar(20));",user, user);

            PreparedStatement ps = conn.prepareStatement(tweets);
            ps.executeUpdate();
            ps.close();
            LOGGER.info("Table is created for user :" + user);
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
    }


    public static void insertTweetsToTable(Connection conn, Status status, String userSource){

        String text = status.getText();
        String userName = status.getUser().getScreenName();
        try{
            if (text.contains("\'") == true){
                text = text.replace("\'", "\''");
            }
            if (userName.contains("\'") == true){
                userName = userName.replace("\'", "\''");
            }

            String insertTweets = String.format("INSERT INTO  " +
                    "tweets_from_%s (id, text) VALUES (%d, '%s') " +
                    "ON CONFLICT DO NOTHING;",userSource, status.getId(), text);

            PreparedStatement ps = conn.prepareStatement(insertTweets);
            ps.executeUpdate();
            ps.close();
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        LOGGER.info("Inserted record for user " + userName);

    }

    public static void cleanTextField(Connection conn, String user){

        String getTweets = String.format("SELECT * FROM " +
                "tweets_from_%s",user);
        try {
            PreparedStatement ps = conn.prepareStatement(getTweets);
            ResultSet resultSet = ps.executeQuery();
            while (resultSet.next()) {

                String tweet = resultSet.getString("text");
                tweet = TextUtils.cleanText(tweet);
                long id = resultSet.getLong("id");
                String updateTweet = String.format("UPDATE   " +
                        "tweets_from_%s SET clean_text = '%s' " +
                        "WHERE id = %d;",user, tweet, id);
                ps = conn.prepareStatement(updateTweet);
                ps.executeUpdate();

            }
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        LOGGER.info("All tweets have been cleaned!");

    }

    public static ResultSet getAllTweets(Connection conn, String user){

        String getTweets = String.format("SELECT * FROM " +
                "tweets_from_%s;",user);
        ResultSet resultSet = null;
        try {
            PreparedStatement ps = conn.prepareStatement(getTweets);
            resultSet = ps.executeQuery();
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        LOGGER.info("All tweets have been loaded!");
        return resultSet;
    }


    public static void insertSentiment(Connection conn, String user, int sentimentScore, String sentimentType, long tweetId){

        LOGGER.info("user " + user);
        LOGGER.info(String.format("tweets_from_%s", user));
        LOGGER.info(String.format("where id = %d", tweetId));


        String getTweet = String.format("UPDATE  " +
                "tweets_from_%s SET CoreNLP_mark = %d ," +
                "CoreNLP_sentiment = '%s' where id = %d;", user, sentimentScore, sentimentType, tweetId);
        try {
            PreparedStatement ps = conn.prepareStatement(getTweet);
            ps.executeUpdate();
            ps.close();
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        LOGGER.info("Inserted the sentiment mark ...");
    }


}
