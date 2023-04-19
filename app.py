import pandas as pd
import numpy as np
import myharmonizer as mh
import streamlit as st
import json
import io
import streamlit_ext as ste

st.markdown("<h1 style='text-align: center; font-size: 65px; color: #4682B4;'>{}</h1>".format('Myharmonizer Application'), unsafe_allow_html=True)
st.markdown("In order to facilitate the comparison between an existing bulk RNA-seq knowledge base and new user data, the myharmonizer package was designed to take 
            a myHarmonizer object output from the [DeepSeqDock framework](https://github.com/bicbioeng/DeepSeqDock) and use the frozen preprocessing, 
            scaling, and transformation methods used to build the knowledge base on new user data. By applying these methods on new user data, the new data 
            is brought into a similar data representation as the existing knowledge base and similarity can be calculated within a theoretically more meaningful space. 
            
            In short, myHarmonizer performs the following:
            * Transform new user datasets into the same representation as the input myHarmonizer knowledge base
            * Calculate similarities between user samples and knowledge samples
            * Visualize similarity matrices
            
            Feel free to either try our examples, or upload your own dataset. Excel or CSV files must be formatted with the first column dedicated to sample labels and the first
            row reserved for gene feature (user input data) or metadata type (user metadata). Only one column of user metadata will be read.") 

examples = st.selectbox('Please select example:',('None', 'SEQC', 'Multi-tissue', 'Multi-cell line'))

meta_json = st.file_uploader("Upload myHarmonizer JSON file:")
input_data = st.file_uploader("Upload user count data (Excel/CSV) file:")
user_meta = st.file_uploader("Upload user metadata (Excel/CSV) file:")

if meta_json != None or examples != 'None':
    if examples == 'Multi-cell line':
            toy_mH = mh.myHarmonizer('examples/myHarmonizer-cells.json')
            newdata = pd.read_csv('examples/cells-test.csv')
            input_user_metadata = pd.read_csv('examples/cells-test-meta.csv', index_col=0).iloc[:,0]
    elif examples == 'SEQC':
            toy_mH = mh.myHarmonizer('examples/myHarmonizer-seqc.json')
            newdata = pd.read_csv('examples/seqc-test.csv')
            input_user_metadata = pd.read_csv('examples/seqc-test-meta.csv', index_col=0).iloc[:,0]
    elif examples == 'Multi-tissue':
            toy_mH = mh.myHarmonizer('examples/myHarmonizer-tissue.json')
            newdata = pd.read_csv('examples/tissue-test.csv')
            input_user_metadata = pd.read_csv('examples/tissue-test-meta.csv', index_col=0).iloc[:,0]
    else:
            json.dump(json.load(meta_json), open('myHarmonizer.json','w'))
            # Build toy myHarmonizer
            toy_mH = mh.myHarmonizer('myHarmonizer.json')
            if input_data.name.split('.')[-1] == 'csv':
                newdata = pd.read_csv(input_data)
            else:
                newdata = pd.read_excel(input_data)
    # Get User Metadata
    input_user_metadata = None
    if user_meta is not None:
        if user_meta.name.split('.')[-1] == 'csv':
            input_user_metadata = pd.read_csv(user_meta, index_col=0).iloc[:,0]
        else:
            input_user_metadata = pd.read_excel(user_meta, index_col=0).iloc[:,0]
    # Get a shortened feature list for the toy dataset
    rawfeatures = toy_mH.modelmeta['encoder_metrics']['features']
    index_col = newdata.columns[0]
    
    if newdata[index_col].duplicated().sum() > 0:
        st.error("Check " + index_col + " column : deduplicate values. Remove and reupload the correct excel file")
    else:
        newdata = newdata.set_index(index_col)

        transformeddata = toy_mH.transform(newdata)
        metric_option = st.selectbox('Select similarity metric:',('Pearson', 'Spearman', 'CCC', 'Euclidean', 'Manhattan', 'Cosine'))
        print(metric_option)
        pearson_sim = mh.similarity(transformeddata, toy_mH.data, metric=metric_option)
            
        # Examine metadata in myHarmonizer object
        #toy_mH.metadata
        st.markdown("Rows are user data samples and columns are knowledge base data samples. For Pearson, Spearman, and CCC metrics, 1 indicates perfect
            correlation or agreement, 0 indicates no relationship, and -1 indicates a negative relationship. For Euclidean, Manhattan, and Cosine metrics,
            a value of 0 indicates that there is no distance between the samples.")
        pearson_sim

        ste.download_button('Download CSV file', toy_mH.metadata.to_csv(index=False), file_name='metadata.csv', mime='text/csv')
        metadata_option = st.selectbox('Select knowledge base metadata to visualize:',tuple(toy_mH.metadata.columns))
        # Plot heatmap
        input_user_metadata
        fig1 = mh.heatmap(pearson_sim, toy_mH, user_metadata=input_user_metadata, kb_metadata=metadata_option)
        
        st.markdown("Heatmap rows are user data samples and columns are knowledge base data samples. For Pearson, Spearman, and CCC metrics, 1 indicates perfect
            correlation or agreement, 0 indicates no relationship, and -1 indicates a negative relationship. For Euclidean, Manhattan, and Cosine metrics,
            a value of 0 indicates that there is no distance between the samples.")
        st.pyplot(fig1)
        img = io.BytesIO()
        fig1.savefig(img, format='png')
        ste.download_button('Download heatmap image', data=img, file_name='heatmap.png', mime='image/png')
