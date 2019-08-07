package com.mazhara.utils.postre;

import com.mazhara.utils.prepocess.TextUtils;
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

//    public static void createTables(Connection conn, String user){
//
//        try{
//            String friends = String.format("CREATE TABLE IF NOT EXISTS " +
//                    "%s_friends (user_id NUMERIC NOT NULL PRIMARY KEY, screen_name varchar(225) " +
//                            "NOT NULL UNIQUE)",user);
//            String tweets = String.format("CREATE TABLE IF NOT EXISTS " +
//                    "tweets_from_%s_friends (id NUMERIC NOT NULL PRIMARY KEY, text varchar(225) " +
//                    "NOT NULL," +
//                    "user_id NUMERIC," +
//                    "FOREIGN KEY (user_id) REFERENCES %s_friends (user_id))",user, user);
//
//            PreparedStatement ps = conn.prepareStatement(friends);
//            ps.executeUpdate();
//            ps = conn.prepareStatement(tweets);
//            ps.executeUpdate();
//            ps.close();
//            LOGGER.info("Tables are created for user :" + user);
//        }catch (SQLException e) {
//            System.out.println(e.getMessage());
//        }
//    }

    public static void createReplyTable(Connection conn, String user){

        try{
            String dropTable = String.format("DROP TABLE IF EXISTS replies_from_%s_friends", user);
            String replies = String.format("CREATE TABLE  " +
                            "replies_from_%s_friends " +
                            "(id NUMERIC NOT NULL PRIMARY KEY, original_text varchar(500) NOT NULL," +
                            "clean_after_Java_text varchar(500), clean_after_Python_text varchar(500),"+
                            "screen_name varchar(225), CoreNLP_score NUMERIC," +
                            "CoreNLP_type varchar(25), Vader_score_origin Double precision," +
                            "Vader_type_origin varchar(25), Vader_score_token Double precision," +
                            "Vader_type_token varchar(25), Vader_score_stemmer Double precision," +
                            "Vader_type_stemmer varchar(25), NBClassifier_mark int, SVMClassifier_mark int" +
                            "svmclassifier_sentiment varchar(10), NBClassifier_sentiment varchar(10)", user);

            PreparedStatement ps = conn.prepareStatement(dropTable);
            ps.executeUpdate();
            ps= conn.prepareStatement(replies);
            ps.executeUpdate();
            ps.close();
            LOGGER.info("Table are created for user :" + user);
        }catch (SQLException e) {
            System.out.println(e.getMessage());
        }
    }

//    public static void insertTweets(Connection conn, Status status, String userSource){
//        String text = status.getText();
//        String userName = status.getUser().getScreenName();
//        try{
//            if (text.contains("\'") == true){
//                text = text.replace("\'", "\''");
//            }
//            if (userName.contains("\'") == true){
//                userName = userName.replace("\'", "\''");
//            }
//
//            String insertFriends = String.format("INSERT INTO  " +
//                    "%s_friends (user_id, screen_name) VALUES(%d, '%s') " +
//                    "ON CONFLICT DO NOTHING;",userSource, status.getUser().getId(), userName);
//            String insertTweets = String.format("INSERT INTO  " +
//                    "tweets_from_%s_friends (id, text, user_id) VALUES (%d, '%s', %d) " +
//                    "ON CONFLICT DO NOTHING;",userSource, status.getId(), text, status.getUser().getId());
//            System.out.println(insertFriends);
//            System.out.println(insertTweets);
//
//            PreparedStatement ps = conn.prepareStatement(insertFriends);
//            ps.executeUpdate();
//            ps = conn.prepareStatement(insertTweets);
//            ps.executeUpdate();
//            ps.close();
//        }catch (SQLException e) {
//            System.out.println(e.getMessage());
//        }
//        LOGGER.info("Inserted record for user " + userName);
//
//    }

    public static void insertTweetsToReplyTable(Connection conn, Status status, String userSource){
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
                    "replies_from_%s_friends (id, original_text, screen_name) VALUES (%d, '%s', '%s') " +
                    "ON CONFLICT DO NOTHING;",userSource, status.getId(), text, status.getUser().getScreenName());

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
                "replies_from_%s_friends",user);
        try {
            PreparedStatement ps = conn.prepareStatement(getTweets);
            ResultSet resultSet = ps.executeQuery();
            while (resultSet.next()) {

                String tweet = resultSet.getString("original_text");
                tweet = TextUtils.cleanText(tweet);
                long id = resultSet.getLong("id");
                String updateTweet = String.format("UPDATE   " +
                        "replies_from_%s_friends SET clean_after_Java_text = '%s' " +
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
                "replies_from_%s_friends;",user);
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
        LOGGER.info(String.format("replies_from_%s_friends", user));
        LOGGER.info(String.format("where id = %d", tweetId));


        String getTweet = String.format("UPDATE  " +
                "replies_from_%s_friends SET CoreNLP_score = %d ," +
                "CoreNLP_type = '%s' where id = %d;", user, sentimentScore, sentimentType, tweetId);
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
