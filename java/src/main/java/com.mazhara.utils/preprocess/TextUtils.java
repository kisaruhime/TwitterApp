package com.mazhara.utils.preprocess;

public class TextUtils {

    public static String cleanText(String str){
        str = str.toLowerCase();
        str = str.replaceAll("[0-9]|http\\S+|www\\S+|rt|@\\w+|\\p{Punct}|&amp", "");

        return str;
    }

}
